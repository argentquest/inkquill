"use client";

import { useEditor, EditorContent, type Editor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import Link from "@tiptap/extension-link";
import Placeholder from "@tiptap/extension-placeholder";
import {
  Bold,
  Italic,
  UnderlineIcon,
  List,
  ListOrdered,
  Quote,
  Code,
  Code2,
  Heading1,
  Heading2,
  Heading3,
  Link2,
  Link2Off,
  Minus,
  RotateCcw,
  RotateCw,
} from "lucide-react";
import { useCallback, useEffect } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type EditorVariant = "full" | "compact";

interface RichTextEditorProps {
  value: string;
  onChange: (html: string) => void;
  placeholder?: string;
  disabled?: boolean;
  variant?: EditorVariant;
  className?: string;
  minHeight?: string;
}

// ---------------------------------------------------------------------------
// Toolbar button
// ---------------------------------------------------------------------------

function ToolbarBtn({
  onClick,
  active,
  disabled,
  title,
  children,
}: {
  onClick: () => void;
  active?: boolean;
  disabled?: boolean;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <button
      className={`flex h-7 w-7 items-center justify-center rounded-lg text-ink-700 transition ${
        active
          ? "bg-ink-900 text-paper"
          : "hover:bg-black/[0.06] hover:text-ink-900"
      } disabled:pointer-events-none disabled:opacity-40`}
      disabled={disabled}
      onMouseDown={(e) => {
        e.preventDefault();
        onClick();
      }}
      title={title}
      type="button"
    >
      {children}
    </button>
  );
}

function Divider() {
  return <div className="h-5 w-px bg-black/10" />;
}

// ---------------------------------------------------------------------------
// Toolbar
// ---------------------------------------------------------------------------

function Toolbar({ editor, variant }: { editor: Editor; variant: EditorVariant }) {
  const setLink = useCallback(() => {
    const previous = editor.getAttributes("link").href as string | undefined;
    const url = window.prompt("URL", previous ?? "https://");
    if (url === null) return;
    if (url === "") {
      editor.chain().focus().extendMarkRange("link").unsetLink().run();
      return;
    }
    editor.chain().focus().extendMarkRange("link").setLink({ href: url, target: "_blank" }).run();
  }, [editor]);

  const isLink = editor.isActive("link");

  return (
    <div className="flex flex-wrap items-center gap-0.5 border-b border-black/8 bg-ink-900/[0.02] px-2 py-1.5">
      {/* Undo / Redo */}
      <ToolbarBtn
        disabled={!editor.can().undo()}
        onClick={() => editor.chain().focus().undo().run()}
        title="Undo"
      >
        <RotateCcw className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        disabled={!editor.can().redo()}
        onClick={() => editor.chain().focus().redo().run()}
        title="Redo"
      >
        <RotateCw className="size-3.5" />
      </ToolbarBtn>

      <Divider />

      {/* Headings — full variant only */}
      {variant === "full" && (
        <>
          <ToolbarBtn
            active={editor.isActive("heading", { level: 1 })}
            onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
            title="Heading 1"
          >
            <Heading1 className="size-3.5" />
          </ToolbarBtn>
          <ToolbarBtn
            active={editor.isActive("heading", { level: 2 })}
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
            title="Heading 2"
          >
            <Heading2 className="size-3.5" />
          </ToolbarBtn>
          <ToolbarBtn
            active={editor.isActive("heading", { level: 3 })}
            onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
            title="Heading 3"
          >
            <Heading3 className="size-3.5" />
          </ToolbarBtn>
          <Divider />
        </>
      )}

      {/* Inline marks */}
      <ToolbarBtn
        active={editor.isActive("bold")}
        onClick={() => editor.chain().focus().toggleBold().run()}
        title="Bold"
      >
        <Bold className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={editor.isActive("italic")}
        onClick={() => editor.chain().focus().toggleItalic().run()}
        title="Italic"
      >
        <Italic className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={editor.isActive("underline")}
        onClick={() => editor.chain().focus().toggleUnderline().run()}
        title="Underline"
      >
        <UnderlineIcon className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={editor.isActive("code")}
        onClick={() => editor.chain().focus().toggleCode().run()}
        title="Inline code"
      >
        <Code className="size-3.5" />
      </ToolbarBtn>

      <Divider />

      {/* Lists */}
      <ToolbarBtn
        active={editor.isActive("bulletList")}
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        title="Bullet list"
      >
        <List className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={editor.isActive("orderedList")}
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        title="Numbered list"
      >
        <ListOrdered className="size-3.5" />
      </ToolbarBtn>

      <Divider />

      {/* Block elements */}
      <ToolbarBtn
        active={editor.isActive("blockquote")}
        onClick={() => editor.chain().focus().toggleBlockquote().run()}
        title="Blockquote"
      >
        <Quote className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={editor.isActive("codeBlock")}
        onClick={() => editor.chain().focus().toggleCodeBlock().run()}
        title="Code block"
      >
        <Code2 className="size-3.5" />
      </ToolbarBtn>

      {/* Horizontal rule — full only */}
      {variant === "full" && (
        <ToolbarBtn
          onClick={() => editor.chain().focus().setHorizontalRule().run()}
          title="Horizontal rule"
        >
          <Minus className="size-3.5" />
        </ToolbarBtn>
      )}

      <Divider />

      {/* Link */}
      <ToolbarBtn
        active={isLink}
        onClick={setLink}
        title={isLink ? "Edit link" : "Add link"}
      >
        <Link2 className="size-3.5" />
      </ToolbarBtn>
      {isLink && (
        <ToolbarBtn
          onClick={() => editor.chain().focus().unsetLink().run()}
          title="Remove link"
        >
          <Link2Off className="size-3.5" />
        </ToolbarBtn>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function RichTextEditor({
  value,
  onChange,
  placeholder = "Write something…",
  disabled = false,
  variant = "full",
  className = "",
  minHeight = "12rem",
}: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: variant === "full" ? { levels: [1, 2, 3] } : false,
        horizontalRule: variant === "full" ? {} : false,
        codeBlock: {},
      }),
      Underline,
      Link.configure({ openOnClick: false, autolink: true }),
      Placeholder.configure({ placeholder }),
    ],
    content: value,
    editable: !disabled,
    onUpdate({ editor }) {
      onChange(editor.getHTML());
    },
    immediatelyRender: false,
  });

  // Sync external value changes (e.g. when loading a post to edit)
  useEffect(() => {
    if (!editor) return;
    const current = editor.getHTML();
    if (value !== current && value !== "<p></p>") {
      editor.commands.setContent(value, false);
    }
  }, [value, editor]);

  // Sync disabled state
  useEffect(() => {
    editor?.setEditable(!disabled);
  }, [disabled, editor]);

  return (
    <div
      className={`overflow-hidden rounded-2xl border border-black/10 bg-[#fcfaf6] transition focus-within:border-amber-600 ${disabled ? "opacity-50 pointer-events-none" : ""} ${className}`}
      data-testid="rich-text-editor"
    >
      {editor && <Toolbar editor={editor} variant={variant} />}
      <EditorContent
        className="rte-content px-4 py-3"
        editor={editor}
        style={{ minHeight }}
      />
    </div>
  );
}
