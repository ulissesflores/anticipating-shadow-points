-- Hanging indent for the reference list (APA 7): every paragraph between a
-- "References" heading and the next heading or horizontal rule. Bare URLs in
-- those paragraphs become links, so LaTeX (xurl) can break them at the margin.
local in_refs = false

function Pandoc(doc)
  local out = {}
  for _, b in ipairs(doc.blocks) do
    if b.t == "Header" then
      in_refs = pandoc.utils.stringify(b):match("^References") ~= nil
      table.insert(out, b)
    elseif b.t == "HorizontalRule" then
      in_refs = false
      table.insert(out, b)
    elseif in_refs and b.t == "Para" then
      b = b:walk({
        Str = function(s)
          local url, tail = s.text:match("^(https?://.-)([.,;]?)$")
          if url then
            return { pandoc.Link(url, url), pandoc.Str(tail) }
          end
        end,
      })
      if FORMAT:match("latex") then
        table.insert(b.content, 1, pandoc.RawInline("latex", "\\noindent\\hangindent=0.5in\\hangafter=1 "))
        table.insert(out, b)
      elseif FORMAT:match("docx") then
        table.insert(out, pandoc.Div({b}, {["custom-style"] = "Bibliography"}))
      else
        table.insert(out, b)
      end
    else
      table.insert(out, b)
    end
  end
  doc.blocks = out
  return doc
end
