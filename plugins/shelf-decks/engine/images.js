/* Deck engine — read an image's pixel size from its PNG or JPEG header.
   Replaces the macOS-only `sips -g pixelWidth` call so the PPTX renderer runs
   on Windows and Linux too. */

const fs = require("fs");

function imageSize(file) {
  const b = fs.readFileSync(file);
  // PNG: signature, then the IHDR chunk holds width and height (big-endian).
  if (b.length > 24 && b.readUInt32BE(0) === 0x89504e47) {
    return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), type: "png" };
  }
  // JPEG: walk the markers to the first start-of-frame (SOF0..SOF15 bar DHT/JPG/DAC).
  if (b.length > 4 && b[0] === 0xff && b[1] === 0xd8) {
    let i = 2;
    while (i + 9 < b.length) {
      if (b[i] !== 0xff) { i++; continue; }
      const m = b[i + 1];
      if (m === 0xd8 || m === 0x01 || (m >= 0xd0 && m <= 0xd7)) { i += 2; continue; }
      const len = b.readUInt16BE(i + 2);
      if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) {
        return { w: b.readUInt16BE(i + 7), h: b.readUInt16BE(i + 5), type: "jpeg" };
      }
      i += 2 + len;
    }
  }
  throw new Error(`Cannot read the size of ${file}: use a PNG or JPEG image.`);
}

module.exports = { imageSize };
