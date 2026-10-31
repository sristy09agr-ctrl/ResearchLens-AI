
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
  Check
} from "lucide-react";

function ResearchAssistant({ papers = [] }) {
  const [question, setQuestion] = useState("");
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);

  const [showPaperSelector, setShowPaperSelector] = useState(false);
  const [selectedPapers, setSelectedPapers] = useState([]);

  const previousPapersRef = useRef([]);

  // Keep the selected paper list synchronized with My Papers.
  // Newly uploaded papers are automatically selected.
  useEffect(() => {
    const previousPapers = previousPapersRef.current;

    const newlyAddedPapers = papers.filter(
      (paper) => !previousPapers.includes(paper)
    );

    setSelectedPapers((previous) => {
      const remainingSelectedPapers = previous.filter(
        (paper) => papers.includes(paper)
      );

      return [
        ...remainingSelectedPapers,
        ...newlyAddedPapers
      ];
    });

    previousPapersRef.current = papers;
  }, [papers]);

  const activeConversation = conversations.find(
    (conversation) => conversation.id === activeConversationId
  );

  const messages = activeConversation?.messages || [];

  const suggestions = [
    "What are the major research gaps in my papers?",
    "Compare the methodologies used in these studies.",
    "What are the limitations of the proposed approaches?",
    "Summarize the key findings across my papers."
  ];

  const startNewConversation = () => {
    setActiveConversationId(null);
    setQuestion("");
  };

  const openConversation = (id) => {
    setActiveConversationId(id);
    setQuestion("");
  };

  const deleteConversation = (id) => {
    setConversations((previous) =>
      previous.filter((conversation) => conversation.id !== id)
    );

    if (activeConversationId === id) {
      setActiveConversationId(null);
      setQuestion("");
    }
  };

  const togglePaperSelection = (paper) => {
    setSelectedPapers((previous) => {
      if (previous.includes(paper)) {
        return previous.filter((item) => item !== paper);
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

  const handleSubmit = (event) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) return;

    const newMessage = {
      role: "user",
      content: trimmedQuestion
    };

    if (activeConversationId === null) {
      const newId = Date.now();

      const newConversation = {
        id: newId,
        title:
          trimmedQuestion.length > 35
            ? trimmedQuestion.substring(0, 35) + "..."
            : trimmedQuestion,
        messages: [newMessage]
      };

      setConversations((previous) => [
        newConversation,
        ...previous
      ]);

      setActiveConversationId(newId);
    } else {
      setConversations((previous) =>
        previous.map((conversation) =>
          conversation.id === activeConversationId
            ? {
                ...conversation,
                messages: [
                  ...conversation.messages,
                  newMessage
                ]
              }
            : conversation
        )
      );
    }

    setQuestion("");
  };

  return (
    <div className="flex min-h-[calc(100vh-80px)] bg-[#080b14] text-white">

      {/* SIDEBAR */}
      <aside className="hidden lg:flex w-64 shrink-0 border-r border-white/10 bg-[#0c1020] flex-col p-5">

        <button
          onClick={startNewConversation}
          className="flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-500 rounded-xl px-4 py-3 text-sm font-medium transition"
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
                  onClick={() => openConversation(conversation.id)}
                  className="flex-1 min-w-0 text-left px-3 py-3 text-sm truncate"
                  title={conversation.title}
                >
                  <span className="flex items-center gap-2">
                    <MessageSquare size={15} className="shrink-0" />
                    <span className="truncate">
                      {conversation.title}
                    </span>
                  </span>
                </button>

                <button
                  onClick={() => deleteConversation(conversation.id)}
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
              onClick={() => setShowPaperSelector((previous) => !previous)}
              className="flex items-center gap-2 text-xs text-gray-300 border border-white/10 hover:border-violet-400/40 bg-[#111729] rounded-lg px-3 py-2 transition"
            >
              <FileText size={15} className="text-violet-400" />

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
                        const isSelected = selectedPapers.includes(paper);

                        return (
                          <button
                            key={`${paper.name}-${index}`}
                            onClick={() => togglePaperSelection(paper)}
                            className="w-full flex items-center gap-3 p-3 rounded-lg text-left hover:bg-white/5 transition"
                          >

                            <div
                              className={`w-5 h-5 shrink-0 rounded-md border flex items-center justify-center ${
                                isSelected
                                  ? "bg-violet-600 border-violet-600"
                                  : "border-white/20"
                              }`}
                            >
                              {isSelected && (
                                <Check size={13} />
                              )}
                            </div>

                            <FileText
                              size={17}
                              className="text-violet-400 shrink-0"
                            />

                            <span className="text-xs text-gray-300 truncate">
                              {paper.name}
                            </span>

                          </button>
                        );
                      })}

                    </div>
                  </>

                )}

                <div className="border-t border-white/10 p-3">

                  <button
                    onClick={() => setShowPaperSelector(false)}
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

              <BookOpen size={14} className="text-violet-400 shrink-0" />

              <span>
                Selected for research:
              </span>

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
                    <BrainCircuit size={32} className="text-violet-400" />
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
                    <Sparkles size={16} className="text-violet-400" />
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
                  <div key={index} className="flex gap-4">

                    <div className="w-9 h-9 shrink-0 rounded-xl bg-violet-500/15 text-violet-400 flex items-center justify-center">
                      <BrainCircuit size={19} />
                    </div>

                    <div className="flex-1 min-w-0">

                      <p className="text-xs text-gray-500 mb-2">
                        Your research question
                      </p>

                      <p className="text-gray-200 leading-relaxed">
                        {message.content}
                      </p>

                      <div className="mt-5 border border-amber-500/20 bg-amber-500/[0.05] rounded-xl p-4">

                        <p className="text-amber-300 text-sm font-medium">
                          Backend connection pending
                        </p>

                        <p className="text-gray-400 text-xs mt-2 leading-relaxed">
                          Your question has been saved in this conversation.
                          AI-generated answers and paper citations will appear
                          here once the research engine API is connected.
                        </p>

                      </div>

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
                  onChange={(event) => setQuestion(event.target.value)}
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      !event.shiftKey
                    ) {
                      event.preventDefault();
                      handleSubmit(event);
                    }
                  }}
                  placeholder="Ask anything about your research papers..."
                  rows={2}
                  className="w-full bg-transparent resize-none outline-none text-sm text-white placeholder:text-gray-500 p-2"
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
                    disabled={!question.trim()}
                    className="bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed p-3 rounded-xl transition"
                    title="Send question"
                  >
                    <Send size={17} />
                  </button>

                </div>
              </div>

            </form>

            <p className="text-center text-gray-600 text-[11px] mt-3">
              AI-generated answers and source citations will be enabled
              after backend integration.
            </p>

          </div>
        </div>

      </main>
    </div>
  );
}

export default ResearchAssistant;
