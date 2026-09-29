"""
Nexus Dashboard — Standalone HTTP Server
Serves the single-page dashboard and JSON API endpoints.
Run with: python scripts/run_dashboard.py
"""
import http.server
import socketserver
import json
import os
import sys
import traceback

PORT = 8090
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


class NexusHandler(http.server.SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        # Suppress per-request noise; only show errors
        if "200" not in (args[1] if len(args) > 1 else ""):
            super().log_message(format, *args)

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, msg, status=500):
        self._send_json({"error": msg}, status=status)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        os.chdir(BASE_DIR)

        if self.path == "/" or self.path == "/index.html":
            html_path = os.path.join(
                BASE_DIR, "nexus", "dashboard", "templates", "index.html"
            )
            try:
                with open(html_path, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:
                self._send_error_json(str(exc))

        elif self.path == "/api/benchmark":
            path = os.path.join(BASE_DIR, "experiments", "results_raw.json")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self._send_json(json.load(f))
            except FileNotFoundError:
                self._send_json([])
            except Exception as exc:
                self._send_error_json(str(exc))

        elif self.path == "/api/registry":
            path = os.path.join(BASE_DIR, "vector_index", "compressed_schemas.json")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Return the flat list of schema objects (not the wrapper dict)
                schemas = data.get("schemas", data) if isinstance(data, dict) else data
                self._send_json(schemas)
            except FileNotFoundError:
                self._send_json([])
            except Exception as exc:
                self._send_error_json(str(exc))

        elif self.path == "/api/cicd_status":
            path = os.path.join(BASE_DIR, "vector_index", "index_manifest.json")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self._send_json(json.load(f))
            except FileNotFoundError:
                self._send_json({})
            except Exception as exc:
                self._send_error_json(str(exc))

        else:
            # Fallback to static file serving
            self.path = self.path.lstrip("/")
            super().do_GET()

    def do_POST(self):
        os.chdir(BASE_DIR)

        if self.path == "/api/analyze":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                payload = json.loads(body)
                query = payload.get("query", "").strip()
                if not query:
                    self._send_error_json("query field is required", status=400)
                    return

                # Lazy import so server starts fast without loading ML models
                from nexus.orchestration.agentic_loop import run_agentic_loop
                result = run_agentic_loop(query)
                self._send_json(result)

            except Exception as exc:
                traceback.print_exc()
                self._send_error_json(str(exc))
        else:
            self._send_error_json("Not found", status=404)


def run_server(start_port: int = PORT):
    os.chdir(BASE_DIR)

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    port = start_port
    while port < start_port + 10:
        try:
            with ReusableTCPServer(("", port), NexusHandler) as httpd:
                print(f"  NEXUS Dashboard running at  http://localhost:{port}")
                print(f"  Press Ctrl+C to stop.\n")
                httpd.serve_forever()
            break
        except OSError as exc:
            print(f"  Port {port} unavailable ({exc}), trying {port + 1}...")
            port += 1


if __name__ == "__main__":
    run_server()
