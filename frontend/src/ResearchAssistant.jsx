
import { useState, useEffect, useRef } from "react";
import {
  BrainCircuit,
  Send,
  Plus,
  FileText,
  Sparkles,
  ChevronDown,
  BookOpen,
  ShieldCheck,
  Microscope,
  Trash2,
  MessageSquare,
  Check,
  LoaderCircle,
  ExternalLink
} from "lucide-react";

// ==========================================
// MARKDOWN FORMATTING
// ==========================================

function cleanMarkdown(text) {
  return String(text || "")
    .replace(/\\([#*_\-`])/g, "$1")
    .replace(/\\\./g, ".")
    .replace(/\\!/g, "!");
}

function renderInline(text, keyPrefix = "inline") {
  const parts = text.split(
    /(\*\*.*?\*\*|__.*?__|`[^`]+`|\*[^*]+\*|_[^_]+_)/g
  );

  return parts.map((part, index) => {
    const key = `${keyPrefix}-${index}`;

    if (
      (part.startsWith("**") && part.endsWith("**")) ||
      (part.startsWith("__") && part.endsWith("__"))
    ) {
      return <strong key={key}>{part.slice(2, -2)}</strong>;
    }

    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={key}
          className="bg-black/30 text-violet-300 px-1.5 py-0.5 rounded text-xs"
        >
          {part.slice(1, -1)}
        </code>
      );
    }

    if (
      (part.startsWith("*") && part.endsWith("*")) ||
      (part.startsWith("_") && part.endsWith("_"))
    ) {
      return <em key={key}>{part.slice(1, -1)}</em>;
    }

    return part;
  });
}

function MarkdownContent({ content }) {
  const lines = cleanMarkdown(content).split("\n");
  const elements = [];

  let index = 0;

  while (index < lines.length) {
    const line = lines[index].trim();

    if (!line) {
      index++;
      continue;
    }

    // Horizontal rule
    if (/^(-{3,}|\*{3,}|_{3,})$/.test(line)) {
      elements.push(
        <hr key={`hr-${index}`} className="border-white/10 my-5" />
      );
      index++;
      continue;
    }

    // Headings
    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);

    if (headingMatch) {
      const level = headingMatch[1].length;

      const headingClasses = {
        1: "text-xl font-bold",
        2: "text-lg font-bold",
        3: "text-base font-semibold",
        4: "text-sm font-semibold",
        5: "text-sm font-medium",
        6: "text-sm font-medium"
      };

      elements.push(
        <div
          key={`heading-${index}`}
          className={`${headingClasses[level]} text-white mt-5 mb-3`}
        >
          {renderInline(headingMatch[2], `heading-${index}`)}
        </div>
      );

      index++;
      continue;
    }

    // Unordered lists
    if (/^[-*+]\s+/.test(line)) {
      const items = [];

      while (
        index < lines.length &&
        /^[-*+]\s+/.test(lines[index].trim())
      ) {
        const item = lines[index]
          .trim()
          .replace(/^[-*+]\s+/, "");

        items.push(
          <li key={`ul-${index}`}>
            {renderInline(item, `ul-${index}`)}
          </li>
        );

        index++;
      }

      elements.push(
        <ul
          key={`list-${index}`}
          className="list-disc pl-6 space-y-2 my-3 text-gray-200"
        >
          {items}
        </ul>
      );

      continue;
    }

    // Numbered lists
    if (/^\d+[.)]\s+/.test(line)) {
      const items = [];

      while (
        index < lines.length &&
        /^\d+[.)]\s+/.test(lines[index].trim())
      ) {
        const item = lines[index]
          .trim()
          .replace(/^\d+[.)]\s+/, "");

        items.push(
          <li key={`ol-${index}`}>
            {renderInline(item, `ol-${index}`)}
          </li>
        );

        index++;
      }

      elements.push(
        <ol
          key={`ordered-${index}`}
          className="list-decimal pl-6 space-y-2 my-3 text-gray-200"
        >
          {items}
        </ol>
      );

      continue;
    }

    // Paragraphs
    const paragraph = [line];
    index++;

    while (
      index < lines.length &&
      lines[index].trim() &&
      !/^(#{1,6}\s+|[-*+]\s+|\d+[.)]\s+|(-{3,}|\*{3,}|_{3,})$)/.test(
        lines[index].trim()
      )
    ) {
      paragraph.push(lines[index].trim());
      index++;
    }

    elements.push(
      <p
        key={`paragraph-${index}`}
        className="text-gray-200 leading-7 my-3"
      >
        {renderInline(paragraph.join(" "), `paragraph-${index}`)}
      </p>
    );
  }

  return <div className="text-sm">{elements}</div>;
}

// ==========================================
// MAIN RESEARCH ASSISTANT
// ==========================================

function ResearchAssistant({ papers = [] }) {
  const [question, setQuestion] = useState("");
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);

  const [showPaperSelector, setShowPaperSelector] = useState(false);
  const [selectedPapers, setSelectedPapers] = useState([]);
  const [loading, setLoading] = useState(false);

  const previousPapersRef = useRef([]);

  // Synchronize selected papers with My Papers.
  useEffect(() => {
    const previousPapers = previousPapersRef.current;

    const newlyAddedPapers = papers.filter(
      (paper) =>
        !previousPapers.some(
          (previous) =>
            previous.document_id === paper.document_id
        )
    );

    setSelectedPapers((previous) => {
      const remainingSelectedPapers = previous.filter(
        (paper) =>
          papers.some(
            (current) =>
              current.document_id === paper.document_id
          )
      );

      return [...remainingSelectedPapers, ...newlyAddedPapers];
    });

    previousPapersRef.current = papers;
  }, [papers]);

  const activeConversation = conversations.find(
    (conversation) =>
      conversation.id === activeConversationId
  );

  const messages = activeConversation?.messages || [];

  const suggestions = [
    "What are the major research gaps in my papers?",
    "Compare the methodologies used in these studies.",
    "What are the limitations of the proposed approaches?",
    "Summarize the key findings across my papers."
  ];

  const startNewConversation = () => {
    if (loading) return;

    setActiveConversationId(null);
    setQuestion("");
  };

  const openConversation = (id) => {
    if (loading) return;

    setActiveConversationId(id);
    setQuestion("");
  };

  const deleteConversation = (id) => {
    if (loading && activeConversationId === id) return;

    setConversations((previous) =>
      previous.filter(
        (conversation) => conversation.id !== id
      )
    );

    if (activeConversationId === id) {
      setActiveConversationId(null);
      setQuestion("");
    }
  };

  const togglePaperSelection = (paper) => {
    setSelectedPapers((previous) => {
      if (
        previous.some(
          (item) =>
            item.document_id === paper.document_id
        )
      ) {
        return previous.filter(
          (item) =>
            item.document_id !== paper.document_id
        );
      }

      return [...previous, paper];
    });
  };

  const selectAllPapers = () => {
    setSelectedPapers([...papers]);
  };

  const clearPaperSelection = () => {
    setSelectedPapers([]);
  };

  // ==========================================
  // ASK AI API
  // ==========================================

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) return;

    if (selectedPapers.length === 0) {
      alert("Please select at least one research paper.");
      return;
    }

    const documentIds = selectedPapers
      .map((paper) => paper.document_id)
      .filter(Boolean);

    if (documentIds.length === 0) {
      alert("Selected papers do not have valid document IDs.");
      return;
    }

    const conversationId =
      activeConversationId ?? Date.now();

    const assistantMessageId =
      `${Date.now()}-assistant`;

    const userMessage = {
      id: `${Date.now()}-user`,
      role: "user",
      content: trimmedQuestion
    };

    const pendingMessage = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      loading: true
    };

    // Create a new conversation or update an existing one.
    if (activeConversationId === null) {
      const newConversation = {
        id: conversationId,
        title:
          trimmedQuestion.length > 35
            ? trimmedQuestion.substring(0, 35) + "..."
            : trimmedQuestion,
        messages: [userMessage, pendingMessage]
      };

      setConversations((previous) => [
        newConversation,
        ...previous
      ]);

      setActiveConversationId(conversationId);
    } else {
      setConversations((previous) =>
        previous.map((conversation) =>
          conversation.id === conversationId
            ? {
                ...conversation,
                messages: [
                  ...conversation.messages,
                  userMessage,
                  pendingMessage
                ]
              }
            : conversation
        )
      );
    }

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query: trimmedQuestion,
          document_ids: documentIds,
          top_k: 5,
          candidate_k: 30,
          alpha: 0.5
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
            ? JSON.stringify(data.detail)
            : "Unable to generate an answer."
        );
      }

      if (data.status !== "success") {
        throw new Error(
          data.message ||
            "The research engine could not answer."
        );
      }

      // Replace loading message with the actual answer.
      setConversations((previous) =>
        previous.map((conversation) =>
          conversation.id === conversationId
            ? {
                ...conversation,
                messages: conversation.messages.map(
                  (message) =>
                    message.id === assistantMessageId
                      ? {
                          ...message,
                          content: data.answer,
                          citations: data.citations || [],
                          evidenceCount:
                            data.total_evidence_passages,
                          selectedDocuments:
                            data.selected_documents || [],
                          loading: false
                        }
                      : message
                )
              }
            : conversation
        )
      );

    } catch (error) {
      console.error(
        "Research Assistant API error:",
        error
      );

      setConversations((previous) =>
        previous.map((conversation) =>
          conversation.id === conversationId
            ? {
                ...conversation,
                messages: conversation.messages.map(
                  (message) =>
                    message.id === assistantMessageId
                      ? {
                          ...message,
                          content: error.message,
                          error: true,
                          loading: false
                        }
                      : message
                )
              }
            : conversation
        )
      );

    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // UI
  // ==========================================

  return (
    <div className="flex min-h-[calc(100vh-80px)] bg-[#080b14] text-white">

      {/* SIDEBAR */}
      <aside className="hidden lg:flex w-64 shrink-0 border-r border-white/10 bg-[#0c1020] flex-col p-5">

        <button
          onClick={startNewConversation}
          disabled={loading}
          className="flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 rounded-xl px-4 py-3 text-sm font-medium transition"
        >
          <Plus size={18} />
          New Conversation
        </button>

        <p className="text-xs text-gray-500 uppercase tracking-widest mt-9 mb-4">
          Workspace
        </p>

        <button
          onClick={startNewConversation}
          className={`w-full text-left flex items-center gap-3 px-3 py-3 rounded-xl text-sm transition ${
            activeConversationId === null
              ? "bg-violet-500/10 text-violet-300"
              : "text-gray-400 hover:bg-white/5 hover:text-white"
          }`}
        >
          <MessageSquare size={17} />
          Research Assistant
        </button>

        <div className="flex items-center justify-between mt-9 mb-4">
          <p className="text-xs text-gray-500 uppercase tracking-widest">
            Recent Conversations
          </p>

          <span className="text-xs text-gray-600">
            {conversations.length}
          </span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-2">

          {conversations.length === 0 ? (
            <p className="px-3 text-sm text-gray-500">
              No conversations yet.
            </p>
          ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`group flex items-center gap-2 rounded-xl transition ${
                  activeConversationId === conversation.id
                    ? "bg-violet-500/10 text-violet-300"
                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                <button
                  onClick={() =>
                    openConversation(conversation.id)
                  }
                  className="flex-1 min-w-0 text-left px-3 py-3 text-sm truncate"
                  title={conversation.title}
                >
                  <span className="flex items-center gap-2">
                    <MessageSquare
                      size={15}
                      className="shrink-0"
                    />
                    <span className="truncate">
                      {conversation.title}
                    </span>
                  </span>
                </button>

                <button
                  onClick={() =>
                    deleteConversation(conversation.id)
                  }
                  className="p-2 mr-1 text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition"
                  title="Delete conversation"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            ))
          )}

        </div>

        <div className="mt-5 border-t border-white/10 pt-5">
          <div className="flex items-center gap-3 text-gray-400 text-xs">
            <ShieldCheck size={17} />
            Evidence-focused research
          </div>
        </div>

      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 min-w-0 flex flex-col">

        {/* HEADER */}
        <header className="min-h-16 border-b border-white/10 flex items-center justify-between px-5 md:px-8 py-3 shrink-0 gap-3">

          <div className="flex items-center gap-3">
            <div className="bg-violet-500/15 text-violet-400 p-2 rounded-lg">
              <BrainCircuit size={21} />
            </div>

            <div>
              <h2 className="font-semibold text-sm">
                AI Research Assistant
              </h2>

              <p className="text-xs text-gray-500">
                Scientific reasoning workspace
              </p>
            </div>
          </div>

          {/* PAPER SELECTOR */}
          <div className="relative">

            <button
              onClick={() =>
                setShowPaperSelector((previous) => !previous)
              }
              className="flex items-center gap-2 text-xs text-gray-300 border border-white/10 hover:border-violet-400/40 bg-[#111729] rounded-lg px-3 py-2 transition"
            >
              <FileText
                size={15}
                className="text-violet-400"
              />

              Papers: {papers.length}

              <ChevronDown
                size={14}
                className={`transition-transform ${
                  showPaperSelector ? "rotate-180" : ""
                }`}
              />
            </button>

            {showPaperSelector && (
              <div className="absolute right-0 top-full mt-3 w-72 max-w-[85vw] bg-[#111729] border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden">

                <div className="p-4 border-b border-white/10">
                  <h3 className="font-semibold text-sm">
                    Select Research Papers
                  </h3>

                  <p className="text-xs text-gray-500 mt-1">
                    {selectedPapers.length} of {papers.length} papers selected
                  </p>
                </div>

                {papers.length === 0 ? (
                  <div className="p-5 text-center">
                    <FileText
                      size={25}
                      className="text-gray-600 mx-auto"
                    />

                    <p className="text-sm text-gray-400 mt-3">
                      No papers uploaded yet.
                    </p>

                    <p className="text-xs text-gray-600 mt-2">
                      Upload PDFs from the My Papers section.
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">

                      <button
                        onClick={selectAllPapers}
                        className="text-xs text-violet-400 hover:text-violet-300"
                      >
                        Select all
                      </button>

                      <button
                        onClick={clearPaperSelection}
                        className="text-xs text-gray-500 hover:text-white"
                      >
                        Clear selection
                      </button>

                    </div>

                    <div className="max-h-64 overflow-y-auto p-2">

                      {papers.map((paper, index) => {
                        const isSelected = selectedPapers.some(
                          (item) =>
                            item.document_id === paper.document_id
                        );

                        return (
                          <button
                            key={paper.document_id || index}
                            onClick={() =>
                              togglePaperSelection(paper)
                            }
                            className="w-full flex items-center gap-3 p-3 rounded-lg text-left hover:bg-white/5 transition"
                          >
                            <div
                              className={`w-5 h-5 shrink-0 rounded-md border flex items-center justify-center ${
                                isSelected
                                  ? "bg-violet-600 border-violet-600"
                                  : "border-white/20"
                              }`}
                            >
                              {isSelected && <Check size={13} />}
                            </div>

                            <FileText
                              size={17}
                              className="text-violet-400 shrink-0"
                            />

                            <span className="text-xs text-gray-300 truncate">
                              {paper.name ||
                                paper.filename ||
                                "Untitled PDF"}
                            </span>
                          </button>
                        );
                      })}

                    </div>
                  </>
                )}

                <div className="border-t border-white/10 p-3">
                  <button
                    onClick={() =>
                      setShowPaperSelector(false)
                    }
                    className="w-full bg-violet-600 hover:bg-violet-500 rounded-lg py-2 text-xs font-medium transition"
                  >
                    Done
                  </button>
                </div>

              </div>
            )}

          </div>

        </header>

        {/* SELECTED PAPERS SUMMARY */}
        {selectedPapers.length > 0 && (
          <div className="px-5 md:px-8 py-3 border-b border-white/5 bg-[#0c1020]">
            <div className="max-w-4xl mx-auto flex items-center gap-2 text-xs text-gray-400">
              <BookOpen
                size={14}
                className="text-violet-400 shrink-0"
              />

              <span>Selected for research:</span>

              <span className="text-violet-300">
                {selectedPapers.length} paper(s)
              </span>
            </div>
          </div>
        )}

        {/* CHAT AREA */}
        <div className="flex-1 overflow-y-auto">

          <div className="max-w-4xl mx-auto px-5 md:px-8 py-10">

            {messages.length === 0 ? (

              /* WELCOME SCREEN */
              <div className="pt-8 md:pt-16">

                <div className="text-center">
                  <div className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600/30 to-blue-500/20 border border-violet-400/20 flex items-center justify-center">
                    <BrainCircuit
                      size={32}
                      className="text-violet-400"
                    />
                  </div>

                  <p className="text-violet-400 text-xs uppercase tracking-widest font-semibold mt-7">
                    ResearchLens Intelligence
                  </p>

                  <h1 className="text-3xl md:text-5xl font-bold mt-4 leading-tight">
                    Understand research.
                    <br />

                    <span className="bg-gradient-to-r from-violet-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
                      Discover connections.
                    </span>
                  </h1>

                  <p className="text-gray-400 mt-5 max-w-xl mx-auto leading-relaxed">
                    Ask questions across your scientific literature.
                    Discover findings, compare methodologies and
                    explore evidence-backed insights.
                  </p>
                </div>

                {/* SUGGESTED QUESTIONS */}
                <div className="mt-14">

                  <div className="flex items-center gap-2 text-gray-400 text-sm mb-4">
                    <Sparkles
                      size={16}
                      className="text-violet-400"
                    />
                    Suggested research questions
                  </div>

                  <div className="grid sm:grid-cols-2 gap-3">

                    {suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => setQuestion(suggestion)}
                        className="text-left p-5 rounded-xl bg-[#111729] border border-white/10 hover:border-violet-400/40 hover:bg-violet-500/[0.06] transition group"
                      >
                        <p className="text-sm text-gray-300 group-hover:text-white leading-relaxed">
                          {suggestion}
                        </p>

                        <div className="flex justify-end mt-3">
                          <Send
                            size={15}
                            className="text-gray-600 group-hover:text-violet-400"
                          />
                        </div>
                      </button>
                    ))}

                  </div>
                </div>

              </div>

            ) : (

              /* CONVERSATION MESSAGES */
              <div className="space-y-8">

                {messages.map((message, index) => (
                  <div
                    key={message.id || index}
                    className={`flex gap-4 ${
                      message.role === "user"
                        ? "flex-row-reverse"
                        : ""
                    }`}
                  >

                    <div
                      className={`w-9 h-9 shrink-0 rounded-xl flex items-center justify-center ${
                        message.role === "user"
                          ? "bg-blue-500/15 text-blue-400"
                          : "bg-violet-500/15 text-violet-400"
                      }`}
                    >
                      {message.role === "user" ? (
                        <MessageSquare size={19} />
                      ) : (
                        <BrainCircuit size={19} />
                      )}
                    </div>

                    <div className="flex-1 min-w-0">

                      <p className="text-xs text-gray-500 mb-2">
                        {message.role === "user"
                          ? "Your research question"
                          : "ResearchLens AI"}
                      </p>

                      <div
                        className={`rounded-xl p-4 ${
                          message.role === "user"
                            ? "bg-blue-500/[0.08] border border-blue-500/15"
                            : "bg-[#111729] border border-white/10"
                        }`}
                      >

                        {message.loading ? (
                          <div className="flex items-center gap-3 text-violet-300 text-sm">
                            <LoaderCircle
                              size={18}
                              className="animate-spin"
                            />
                            Analyzing your research papers...
                          </div>
                        ) : message.error ? (
                          <p className="text-sm leading-7 text-red-300 whitespace-pre-wrap">
                            {message.content}
                          </p>
                        ) : message.role === "user" ? (
                          <p className="text-sm leading-7 text-gray-200 whitespace-pre-wrap">
                            {message.content}
                          </p>
                        ) : (
                          <MarkdownContent
                            content={message.content}
                          />
                        )}

                      </div>

                      {/* CITATIONS */}
                      {message.citations?.length > 0 && (
                        <div className="mt-5">

                          <div className="flex items-center gap-2 text-sm text-violet-300 font-medium mb-3">
                            <BookOpen size={16} />
                            Sources ({message.citations.length})
                          </div>

                          <div className="space-y-2">

                            {message.citations.map((citation) => (
                              <div
                                key={citation.citation_number}
                                className="flex items-start gap-3 p-3 rounded-xl bg-[#111729] border border-white/10"
                              >

                                <span className="w-7 h-7 shrink-0 rounded-lg bg-violet-500/15 text-violet-300 flex items-center justify-center text-xs font-semibold">
                                  [{citation.citation_number}]
                                </span>

                                <div className="flex-1 min-w-0">

                                  <p className="text-xs text-gray-200 font-medium break-words">
                                    {citation.filename}
                                  </p>

                                  <p className="text-xs text-gray-500 mt-1">
                                    Page {citation.page_start}
                                    {citation.page_end !== citation.page_start
                                      ? `–${citation.page_end}`
                                      : ""}
                                    {" · "}
                                    {citation.section ||
                                      "Unidentified section"}
                                  </p>

                                  <a
                                    href={`/api/documents/${encodeURIComponent(
                                      citation.document_id
                                    )}/download`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="inline-flex items-center gap-1 text-xs text-violet-400 hover:text-violet-300 mt-2"
                                  >
                                    Open source PDF
                                    <ExternalLink size={12} />
                                  </a>

                                </div>
                              </div>
                            ))}

                          </div>

                          <p className="text-xs text-gray-600 mt-3">
                            Based on {message.evidenceCount} retrieved evidence passages.
                          </p>

                        </div>
                      )}

                    </div>
                  </div>
                ))}

              </div>
            )}

          </div>
        </div>

        {/* QUESTION INPUT */}
        <div className="border-t border-white/10 bg-[#0c1020] px-5 md:px-8 py-5">

          <div className="max-w-4xl mx-auto">

            <form onSubmit={handleSubmit}>

              <div className="bg-[#111729] border border-white/10 focus-within:border-violet-500/50 rounded-2xl p-3 transition">

                <textarea
                  value={question}
                  onChange={(event) =>
                    setQuestion(event.target.value)
                  }
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      !event.shiftKey
                    ) {
                      event.preventDefault();
                      event.currentTarget.form?.requestSubmit();
                    }
                  }}
                  placeholder="Ask anything about your research papers..."
                  rows={2}
                  disabled={loading}
                  className="w-full bg-transparent resize-none outline-none text-sm text-white placeholder:text-gray-500 p-2 disabled:opacity-50"
                />

                <div className="flex items-center justify-between mt-2 px-2">

                  <div className="flex items-center gap-3 text-xs text-gray-500">

                    <span className="flex items-center gap-1">
                      <BookOpen size={14} />
                      Research mode
                    </span>

                    <span className="hidden sm:flex items-center gap-1">
                      <Microscope size={14} />
                      Evidence-based
                    </span>

                  </div>

                  <button
                    type="submit"
                    disabled={!question.trim() || loading}
                    className="bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed p-3 rounded-xl transition"
                    title="Send question"
                  >
                    {loading ? (
                      <LoaderCircle
                        size={17}
                        className="animate-spin"
                      />
                    ) : (
                      <Send size={17} />
                    )}
                  </button>

                </div>
              </div>

            </form>

            <p className="text-center text-gray-600 text-[11px] mt-3">
              AI-generated answers grounded in your selected research papers, with source citations.
            </p>

          </div>
        </div>

      </main>
    </div>
  );
}

export default ResearchAssistant;
