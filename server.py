#!/usr/bin/env python3
"""
Simple HTTP server to run the HTML UI for the Loan Application system.
No external dependencies required - uses only Python standard library.
"""

import http.server
import socketserver
import os
import sys
import webbrowser

PORT = 8000
os.chdir(os.path.join(os.path.dirname(__file__), 'ui'))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

    def log_message(self, format, *args):
        # Custom logging
        print(f"[{self.client_address[0]}] {format % args}")

if __name__ == "__main__":
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print("\n" + "="*70)
            print("🏦 LOAN APPLICATION SYSTEM - WEB UI")
            print("="*70)
            print(f"\n✅ Server started successfully!")
            print(f"\n🌐 Open your browser and go to: http://localhost:{PORT}")
            print(f"\n📱 You can now:")
            print(f"   • Fill in loan application details")
            print(f"   • Submit applications for processing")
            print(f"   • View AI-powered loan decisions")
            print(f"   • See detailed analysis and statistics")
            print(f"\n🛑 Press Ctrl+C to stop the server\n")
            print("="*70 + "\n")

            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print("🌐 Browser opening automatically...\n")
            except:
                pass

            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 Server stopped")
        print("="*70 + "\n")
        sys.exit(0)
    except OSError as e:
        print(f"\n❌ Error: {e}")
        print(f"   Port {PORT} might be in use. Try a different port:")
        print(f"   python3 server.py 8080")
        sys.exit(1)
