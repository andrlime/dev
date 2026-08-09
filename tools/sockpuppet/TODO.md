# Future Development

- [ ] Use trio to make the managed VPN client asynchronous. Rationale is this is more extensible than the current version.
- [ ] Resolve signal handling delay in the non-managed backend caused by `rumps.timer(...)` (which was suggested by Claude). There isn't an async solution here because the frontend uses Cocoa and other MacOS internal libraries and cannot be worked around.
