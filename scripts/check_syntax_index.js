const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const scriptRegex = /<script\b[^>]*>([\s\S]*?)<\/script>/gi;
let match;
let i = 0;
while ((match = scriptRegex.exec(html)) !== null) {
  i++;
  const tag = match[0];
  const srcMatch = tag.match(/src=["']([^"']+)["']/);
  if (srcMatch) {
    console.log('Script ' + i + ' (external): ' + srcMatch[1]);
  } else {
    console.log('Script ' + i + ' (inline, length ' + match[1].length + ')');
    try {
      new Function(match[1]);
      console.log('  -> Syntax OK');
    } catch (e) {
      console.error('  -> SYNTAX ERROR in script ' + i + ':', e.message);
    }
  }
}
