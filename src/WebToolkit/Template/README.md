# Web app template (Web Toolkit for FutureBasic)

Copy this folder, rename `Web App.fbeproj` if you like, and write your page in `Pages.incl`:

- `AppTitle`, `AppStarting` (open the database, declare the rules - NO stops the app);
- `BuildPage`: the widgets, and `WebOn` for each event;
- the event functions, and the page's lifecycle (shown, hidden, visible, leaving, the session's end).

Everything else is the toolkit, identical in every app: `Server Window.incl` starts the FastCGI server on
127.0.0.1:9000 and shows what it is doing; the app keeps serving when its window is closed.

Run: build in FutureBasic, start nginx (`nginx -c "$PWD/nginx.conf" -p "$PWD"`), open http://127.0.0.1:8088/.
To keep it running on a server Mac: `com.example.webapp.plist` (a LaunchAgent), and HTTPS in nginx.
To bind pages to a database through business rules, add `Web Binding.incl` and LogicBank for FutureBasic
(see `../../WebToolkitExample`).
