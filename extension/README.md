# LeetTrack Browser Extension

This is the Manifest V3 browser extension for LeetTrack.

## Current Scope

- Runs a content script on LeetCode problem pages.
- Detects the active problem slug and title from the real browser tab.
- Shows the detected problem in the extension popup.

## Local Testing

1. Open Chrome or Brave.
2. Go to `chrome://extensions`.
3. Enable Developer mode.
4. Choose **Load unpacked**.
5. Select the `extension/` folder.
6. Open a LeetCode problem page, then click the LeetTrack extension icon.

The extension does not authenticate or save data yet. Those belong in the next
extension milestone after page detection is reliable.
