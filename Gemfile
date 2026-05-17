source "https://rubygems.org"

# GitHub Pages — Jekyll + plugins.
# Locked to the same versions GitHub Pages uses, so local previews
# match the deployed site. See https://pages.github.com/versions/
gem "github-pages", group: :jekyll_plugins

# just-the-docs theme is loaded via `remote_theme:` in _config.yml; no gem needed locally
# for Pages builds, but listing the plugin gems explicitly helps `bundle exec jekyll serve`.
group :jekyll_plugins do
  gem "jekyll-remote-theme"
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
end

# Windows + JRuby compatibility (harmless on Mac/Linux)
gem "tzinfo", "~> 1.2"
gem "tzinfo-data"
gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]
