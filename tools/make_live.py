"""Turn the editable portfolio draft into the public, read-only site.

Usage: python3 make_live.py <edited-portfolio.html> <output index.html> [theme]
(theme = a file name in tools/themes, e.g. navy)

The draft keeps its in-page editor (edit buttons, download, profile form).
The live copy hides those controls and ignores any edits saved in a visitor's
browser, so every visitor sees exactly the content baked into the file.
"""
import sys

src, out = sys.argv[1], sys.argv[2]
theme = sys.argv[3] if len(sys.argv) > 3 else None
html = open(src, encoding="utf-8").read()

# Ignore localStorage so visitors always see the published content.
old = "stored=localStorage.getItem(key)"
assert html.count(old) == 1, "draft script changed; update make_live.py"
html = html.replace(old, "stored=null")

live_css = """
<style id="live-mode">
#edit-toggle,#project-form,#text-edit-toggle,#export,#story-open,#profile-open,
#portrait-open,.portrait-edit,#contact-form,#text-edit-bar,#text-editor,
.portrait-empty,#personal-statement.pending,.footer-bottom span:last-child{display:none!important}
/* Homepage portrait: frame takes the photo's own shape so nothing is cropped. */
.portrait-frame{height:auto!important;aspect-ratio:auto}
.portrait-frame img{height:auto!important;object-fit:contain!important;display:block}
/* About portrait: never crop, whatever the photo's shape. */
.about-portrait img{max-height:none!important;height:auto!important;object-fit:contain!important}
</style>
"""
if theme:
    # Override the color tokens; every other color is derived from these.
    import os
    css = open(os.path.join(os.path.dirname(__file__), "themes", theme + ".css")).read().strip()
    live_css += "<style id=\"theme\">:root{" + css + "}</style>\n"
assert html.count("</head>") == 1
html = html.replace("</head>", live_css + "</head>")

# Route in-page links without real hash navigation. Previews that load the
# page from srcdoc or a sandboxed frame turn href="#about" into a navigation
# away from the page, so every menu link broke there.
router = """
<script id="live-router">
window.__route=(function(){
  let current='';try{current=location.hash}catch(e){}
  function fire(){window.dispatchEvent(new Event('hashchange'))}
  window.addEventListener('popstate',()=>{try{if(location.hash!==current){current=location.hash;fire()}}catch(e){}});
  document.addEventListener('click',e=>{
    const a=e.target.closest&&e.target.closest('a[href^="#"]');
    if(!a||e.defaultPrevented||e.metaKey||e.ctrlKey||e.shiftKey||e.button)return;
    e.preventDefault();r.hash=a.getAttribute('href');
  },true);
  const r={get hash(){return current},set hash(v){
    v=v?(v[0]==='#'?v:'#'+v):'';if(v===current)return;current=v;
    try{history.pushState(history.state,'',v||location.pathname+location.search)}catch(e){}
    fire()}};
  return r})();
</script>
"""
main_start = html.rfind("<script>")
script = html[main_start:]
assert script.count("location.hash") >= 5, "draft script changed; update make_live.py"
script = script.replace("location.hash", "window.__route.hash")
html = html[:main_start] + router + script

open(out, "w", encoding="utf-8").write(html)
print(f"wrote {out} ({len(html)/1e6:.1f} MB)")
