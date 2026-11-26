#!/usr/bin/env python3
"""Tests the FastCGI core of src/MacTests/FastCGI Test.fb - the portable C between its "FastCGI core" markers - here,
where FutureBasic cannot run: compiled with the C compiler, then

    1. the protocol, by hand: a request made of records (short and long name lengths, the body in pieces, padding, a
       record split across reads), parsed; a response encoded into STDOUT records and END_REQUEST, decoded back
    2. behind a real nginx (when nginx is installed): a small server built from the same core answers nginx's FastCGI,
       and HTTP requests through nginx - GET, POST with a body, a large reply - come back as they should

    python3 tools/check_fastcgi_core.py
"""
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
FB = os.path.join(HERE, '..', 'src', 'MacTests', 'FastCGI Test.fb')
MODULE = os.path.join(HERE, '..', 'src', 'WebToolkit', 'Web Server.incl')

HARNESS = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
%(core)s

static int failures = 0;
#define CHECK(c, what) do { if (c) printf("PASS  %%s\n", what); else { printf("FAIL  %%s\n", what); failures++; } } while (0)

static size_t rec(unsigned char *o, int type, int id, const unsigned char *c, size_t n, int pad) {
    o[0]=1; o[1]=type; o[2]=id>>8; o[3]=id; o[4]=n>>8; o[5]=n; o[6]=pad; o[7]=0;
    memcpy(o+8, c, n); memset(o+8+n, 0, pad); return 8+n+pad;
}
static size_t pair(unsigned char *o, const char *name, const char *value) {
    size_t a=strlen(name), b=strlen(value), at=0;
    if (a<128) o[at++]=a; else { o[at++]=0x80|(a>>24); o[at++]=a>>16; o[at++]=a>>8; o[at++]=a; }
    if (b<128) o[at++]=b; else { o[at++]=0x80|(b>>24); o[at++]=b>>16; o[at++]=b>>8; o[at++]=b; }
    memcpy(o+at,name,a); memcpy(o+at+a,value,b); return at+a+b;
}

static void unit(void) {
    unsigned char req[70000], params[4000], *p = req;
    unsigned char begin[8] = {0,1,1,0,0,0,0,0};          /* RESPONDER, KEEP_CONN */
    char longValue[300]; memset(longValue,'x',299); longValue[299]=0;
    size_t n = 0, total;
    fcgi_request r;
    p += rec(p, FCGI_BEGIN_REQUEST, 7, begin, 8, 0);
    n += pair(params+n, "REQUEST_METHOD", "POST");
    n += pair(params+n, "DOCUMENT_URI", "/event");
    n += pair(params+n, "LONG_VALUE", longValue);       /* a four-byte length */
    p += rec(p, FCGI_PARAMS, 7, params, n, 3);           /* with padding */
    p += rec(p, FCGI_PARAMS, 7, params, 0, 0);
    p += rec(p, FCGI_STDIN, 7, (const unsigned char *)"{\"widget\":", 10, 6);
    p += rec(p, FCGI_STDIN, 7, (const unsigned char *)"\"add\"}", 6, 0);
    p += rec(p, FCGI_STDIN, 7, NULL, 0, 0);
    total = p - req;
    CHECK(fcgi_parse(req, total, &r) == 1, "a whole request parses");
    CHECK(r.requestId == 7 && r.keepConn == 1, "its request id and keep-connection flag");
    CHECK(strcmp(fcgi_param(&r, "REQUEST_METHOD"), "POST") == 0 && strcmp(fcgi_param(&r, "DOCUMENT_URI"), "/event") == 0, "its parameters");
    CHECK(strlen(fcgi_param(&r, "LONG_VALUE")) == 299, "a value longer than 127 bytes (four-byte length)");
    CHECK(r.bodyLength == 16 && strcmp((char *)r.body, "{\"widget\":\"add\"}") == 0, "the body, from two STDIN records");
    fcgi_request_free(&r);
    int partial_ok = 1;
    for (size_t cut = 0; cut < total; cut++) { if (fcgi_parse(req, cut, &r) != 0) partial_ok = 0; fcgi_request_free(&r); }
    CHECK(partial_ok, "every incomplete prefix waits for more (records split across reads)");
    unsigned char bad[16]; memcpy(bad, req, 16); bad[0] = 2;
    CHECK(fcgi_parse(bad, 16, &r) == -1, "a wrong protocol version is refused");
    size_t outLength; char big[150000]; memset(big, 'y', sizeof big);
    unsigned char *out = fcgi_response(7, (unsigned char *)big, sizeof big, &outLength);
    size_t at = 0, got = 0; int records = 0, ended = 0, emptyStdout = 0;
    while (at + 8 <= outLength) {
        size_t len = (out[at+4]<<8)|out[at+5];
        if (out[at+1] == FCGI_STDOUT) { if (len == 0) emptyStdout = 1; got += len; records++; }
        if (out[at+1] == FCGI_END_REQUEST) ended = 1;
        if (((out[at+2]<<8)|out[at+3]) != 7) ended = -1;
        at += 8 + len + out[at+6];
    }
    CHECK(got == sizeof big && records >= 4 && emptyStdout && ended == 1 && at == outLength, "a 150 KB answer: STDOUT records under 64 KB each, the empty STDOUT, END_REQUEST");
    free(out);
}

static void serve(int port) {
    int s = socket(AF_INET, SOCK_STREAM, 0), yes = 1;
    struct sockaddr_in a; memset(&a, 0, sizeof a);
    setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof yes);
    a.sin_family = AF_INET; a.sin_port = htons(port); a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    if (bind(s, (struct sockaddr *)&a, sizeof a) < 0 || listen(s, 16) < 0) { perror("bind"); exit(1); }
    printf("ready\n"); fflush(stdout);
    for (;;) {
        int c = accept(s, NULL, NULL); if (c < 0) continue;
        unsigned char *buf = NULL; size_t len = 0; fcgi_request r; int state = 0;
        for (;;) {
            unsigned char chunk[16384]; ssize_t n = read(c, chunk, sizeof chunk); if (n <= 0) break;
            buf = realloc(buf, len + n); memcpy(buf + len, chunk, n); len += n;
            state = fcgi_parse(buf, len, &r); if (state != 0) break;
        }
        if (state == 1) {
            char *cgi; size_t cgiLength;
            if (strcmp(fcgi_param(&r, "DOCUMENT_URI"), "/big") == 0) {
                cgiLength = 100000 + 64; cgi = malloc(cgiLength + 1);
                int h = sprintf(cgi, "Status: 200 OK\r\nContent-Type: text/plain\r\n\r\n");
                memset(cgi + h, 'z', 100000); cgiLength = h + 100000;
            } else {
                cgi = malloc(4096 + r.bodyLength);
                cgiLength = sprintf(cgi, "Status: 201 Created\r\nContent-Type: text/plain\r\nX-Test: fb\r\n\r\n%%s %%s ?%%s body=%%s",
                    fcgi_param(&r, "REQUEST_METHOD"), fcgi_param(&r, "DOCUMENT_URI"), fcgi_param(&r, "QUERY_STRING"), (char *)r.body);
            }
            size_t outLength; unsigned char *out = fcgi_response(r.requestId, (unsigned char *)cgi, cgiLength, &outLength);
            size_t at = 0; while (at < outLength) { ssize_t n = write(c, out + at, outLength - at); if (n <= 0) break; at += n; }
            free(out); free(cgi); fcgi_request_free(&r);
        }
        free(buf); close(c);
    }
}

int main(int argc, char **argv) {
    if (argc > 1) { serve(atoi(argv[1])); return 0; }
    unit();
    return failures ? 1 : 0;
}
'''

NGINX_CONF = '''
worker_processes 1;
error_log %(dir)s/error.log;
pid %(dir)s/nginx.pid;
events { worker_connections 64; }
http {
    access_log off;
    client_body_temp_path %(dir)s; fastcgi_temp_path %(dir)s; proxy_temp_path %(dir)s; uwsgi_temp_path %(dir)s; scgi_temp_path %(dir)s;
    server {
        listen 127.0.0.1:%(http)d;
        location / {
            include %(params)s;
            fastcgi_pass 127.0.0.1:%(fcgi)d;
        }
    }
}
'''


def core_source(path=FB):
    text = open(path, encoding='utf-8').read().replace('\r', '\n')
    start = text.index('/* --- FastCGI core')
    end = text.index('/* --- end FastCGI core --- */')
    return text[start:end]


def free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main():
    work = tempfile.mkdtemp()
    try:
        src = os.path.join(work, 'fastcgi.c')
        with open(src, 'w') as f:
            f.write(HARNESS % {'core': core_source()})
        exe = os.path.join(work, 'fastcgi')
        build = subprocess.run(['cc', '-std=c99', '-D_DEFAULT_SOURCE', '-Wall', '-Wextra', '-Wno-unused-parameter', '-Werror', '-o', exe, src], capture_output=True, text=True)
        if build.returncode != 0:
            print(build.stderr)
            print('fastcgi core: does not compile')
            return 1
        unit = subprocess.run([exe], capture_output=True, text=True)
        print(unit.stdout, end='')
        failed = unit.returncode != 0
        same = os.path.exists(MODULE) and core_source(MODULE) == core_source()
        print(('PASS  ' if same else 'FAIL  ') + 'the Web Toolkit\'s Web Server.incl carries the same core')
        failed = failed or not same
        nginx = shutil.which('nginx') or ('/usr/sbin/nginx' if os.path.exists('/usr/sbin/nginx') else None)
        params = next((p for p in ('/etc/nginx/fastcgi_params', '/opt/homebrew/etc/nginx/fastcgi_params', '/usr/local/etc/nginx/fastcgi_params') if os.path.exists(p)), None)
        if not nginx or not params:
            print('SKIP  behind nginx: nginx is not installed here')
        else:
            fcgi, http = free_port(), free_port()
            server = subprocess.Popen([exe, str(fcgi)], stdout=subprocess.PIPE, text=True)
            server.stdout.readline()
            conf = os.path.join(work, 'nginx.conf')
            with open(conf, 'w') as f:
                f.write(NGINX_CONF % {'dir': work, 'http': http, 'fcgi': fcgi, 'params': params})
            ng = subprocess.Popen([nginx, '-c', conf, '-p', work, '-g', 'daemon off;'], stderr=subprocess.PIPE)
            time.sleep(0.6)
            try:
                def check(ok, what):
                    nonlocal failed
                    print(('PASS  ' if ok else 'FAIL  ') + what)
                    failed = failed or not ok
                r = urllib.request.urlopen(f'http://127.0.0.1:{http}/hello?x=1')
                body = r.read().decode()
                check(r.status == 201 and r.headers['X-Test'] == 'fb' and body == 'GET /hello ?x=1 body=', 'behind nginx: GET - the status, a header and the parameters arrive')
                r = urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{http}/event', data=b'{"widget":"add"}', method='POST'))
                check(r.read().decode() == 'POST /event ? body={"widget":"add"}', 'behind nginx: POST - the body reaches the program')
                r = urllib.request.urlopen(f'http://127.0.0.1:{http}/big')
                check(len(r.read()) == 100000, 'behind nginx: a 100 KB answer arrives whole')
            finally:
                ng.terminate()
                server.terminate()
        print('fastcgi core: ' + ('FAILURES' if failed else 'all passed'))
        return 1 if failed else 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
