# Web app template (Web Toolkit for FutureBasic)

Copy this folder, rename `Web App.fbeproj` if you like, and write your page in `Pages.incl`:

- `AppTitle`, `AppStarting` (open the database, declare the rules; returning NO stops the app);
- `BuildPage`: the widgets, and `WebOn` for each event;
- the event functions, and the page's lifecycle (shown, hidden, visible, leaving, the session's end).

The rest is the toolkit, the same in every app. `Server Window.incl` starts the FastCGI server on
127.0.0.1:9000 and shows you what it's doing, and the app keeps serving after you close its window.

To run it, build in FutureBasic, start nginx (`nginx -c "$PWD/nginx.conf" -p "$PWD"`) and open
http://127.0.0.1:8088/. On a server Mac, `com.example.webapp.plist` (a LaunchAgent) keeps it running; add
HTTPS in nginx. If you'd like your pages bound to a database through business rules, add `Web Binding.incl`
and LogicBank for FutureBasic (`../../WebToolkitExample` shows how).
