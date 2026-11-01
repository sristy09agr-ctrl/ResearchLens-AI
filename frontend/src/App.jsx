
import { useState, useEffect, useCallback } from "react";
import ResearchAssistant from "./ResearchAssistant";

import {
  BrainCircuit,
  FileText,
  Search,
  ShieldCheck,
  GitCompareArrows,
  ArrowRight,
  Upload,
  Sparkles,
  Microscope,
  BookOpen,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  LayoutDashboard,
  Plus,
  Home,
  MessageSquare,
  Files,
  Trash2,
  ArrowUp,
  Download,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Loader2
} from "lucide-react";

const API_BASE = "/api";
const MAX_FILE_SIZE = 20 * 1024 * 1024;

// Safely read API responses
async function readResponse(response) {
  const text = await response.text();

  if (!text) {
    throw new Error("The server returned an empty response.");
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new Error("The server returned an invalid response.");
  }
}

// --------------------------------------------------
// PAPER CHUNK VIEWER
// --------------------------------------------------

function PaperChunks({ documentId }) {
  const [expanded, setExpanded] = useState(false);
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loaded, setLoaded] = useState(false);

  const loadChunks = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_BASE}/documents/${documentId}/chunks`
      );

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : data.detail?.message || "Could not load extracted text."
        );
      }

      setChunks(data.chunks || []);
      setLoaded(true);

    } catch (err) {
      console.error("Chunk loading error:", err);
      setError(err.message || "Could not load extracted text.");

    } finally {
      setLoading(false);
    }
  };

  const toggleViewer = () => {
    if (expanded) {
      setExpanded(false);
      return;
    }

    setExpanded(true);

    if (!loaded) {
      loadChunks();
    }
  };

  return (
    <div className="mt-4 border-t border-white/10 pt-3">

      <button
        onClick={toggleViewer}
        className="flex items-center justify-between w-full text-sm text-violet-400 hover:text-violet-300 transition"
      >
        <span className="flex items-center gap-2">
          <BookOpen size={17} />
          {expanded ? "Hide extracted content" : "View extracted content"}
        </span>

        {expanded ? (
          <ChevronUp size={18} />
        ) : (
          <ChevronDown size={18} />
        )}
      </button>

      {expanded && (
        <div className="mt-4 space-y-4">

          {loading && (
            <div className="flex items-center justify-center gap-3 py-8 text-gray-400 text-sm">
              <Loader2 size={20} className="animate-spin text-violet-400" />
              Loading extracted text...
            </div>
          )}

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
              <div className="flex items-start gap-3 text-red-300">
                <AlertCircle size={19} className="shrink-0 mt-0.5" />

                <div>
                  <p className="text-sm font-medium">
                    Could not load extracted content
                  </p>

                  <p className="text-xs mt-1 whitespace-pre-line">
                    {error}
                  </p>

                  <button
                    onClick={loadChunks}
                    disabled={loading}
                    className="text-sm underline mt-3 hover:text-white"
                  >
                    Try again
                  </button>
                </div>
              </div>
            </div>
          )}

          {!loading && !error && loaded && chunks.length === 0 && (
            <div className="text-center py-6 text-gray-500 text-sm">
              No extracted chunks are available for this document.
            </div>
          )}

          {!loading && !error && chunks.length > 0 && (
            <>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-xs text-gray-400">
                  {chunks.length} extracted chunks
                </p>

                <button
                  onClick={loadChunks}
                  disabled={loading}
                  className="flex items-center gap-2 text-xs text-gray-400 hover:text-violet-400"
                >
                  <RefreshCw size={13} />
                  Refresh
                </button>
              </div>

              {chunks.map((chunk) => (
                <div
                  key={chunk.chunk_id}
                  className="bg-[#080b14] border border-white/10 rounded-xl p-4"
                >

                  <div className="flex flex-wrap items-center justify-between gap-2 mb-3">

                    <span className="text-sm font-semibold text-violet-300">
                      Chunk {chunk.chunk_id}
                    </span>

                    <span className="text-xs text-gray-500">
                      Page {chunk.page_start}
                      {chunk.page_end !== chunk.page_start
                        ? ` – ${chunk.page_end}`
                        : ""}
                    </span>

                  </div>

                  {chunk.section && (
                    <p className="text-xs text-cyan-400 mb-3">
                      Section: {chunk.section}
                    </p>
                  )}

                  <p className="text-sm text-gray-300 leading-7 whitespace-pre-wrap break-words">
                    {chunk.text}
                  </p>

                  <div className="flex flex-wrap gap-x-5 gap-y-2 mt-4 pt-3 border-t border-white/10 text-xs text-gray-500">

                    {chunk.word_start !== undefined && (
                      <span>
                        Starting word: {chunk.word_start}
                      </span>
                    )}

                    {chunk.word_end !== undefined && (
                      <span>
                        Ending word: {chunk.word_end}
                      </span>
                    )}

                  </div>

                </div>
              ))}
            </>
          )}

        </div>
      )}

    </div>
  );
}

// --------------------------------------------------
// MAIN APP
// --------------------------------------------------

function App() {
  const [page, setPage] = useState("home");
  const [activeTab, setActiveTab] = useState("Overview");

  const [papers, setPapers] = useState([]);
  const [showBackToTop, setShowBackToTop] = useState(false);

  const [loadingPapers, setLoadingPapers] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deletingPaperId, setDeletingPaperId] = useState(null);

  const [paperError, setPaperError] = useState("");
  const [uploadNotice, setUploadNotice] = useState(null);

  // --------------------------------------------------
  // LOAD DOCUMENTS FROM BACKEND
  // --------------------------------------------------

  const loadPapers = useCallback(async () => {
    setLoadingPapers(true);
    setPaperError("");

    try {
      const response = await fetch(`${API_BASE}/documents`);
      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          data.detail?.message ||
          data.detail ||
          "Could not load documents."
        );
      }

      const backendPapers = (data.documents || []).map((document) => ({
        ...document,
        name: document.filename || document.name || "Untitled PDF",
        size: document.file_size || document.size || null
      }));

      setPapers(backendPapers);

    } catch (error) {
      console.error("Document loading error:", error);

      setPaperError(
        error.message || "Could not connect to the backend."
      );

    } finally {
      setLoadingPapers(false);
    }
  }, []);

  useEffect(() => {
    loadPapers();
  }, [loadPapers]);

  // --------------------------------------------------
  // BACK TO TOP
  // --------------------------------------------------

  useEffect(() => {
    const handleScroll = () => {
      setShowBackToTop(window.scrollY > 300);
    };

    window.addEventListener("scroll", handleScroll);

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
  };

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  };

  // --------------------------------------------------
  // LANDING PAGE FEATURES
  // --------------------------------------------------

  const features = [
    {
      icon: BrainCircuit,
      title: "AI Research Assistant",
      description:
        "Ask complex research questions and get intelligent answers grounded in scientific literature."
    },
    {
      icon: GitCompareArrows,
      title: "Paper Comparison",
      description:
        "Compare research papers, methodologies, findings and limitations in one place."
    },
    {
      icon: ShieldCheck,
      title: "Claim Verification",
      description:
        "Verify scientific claims against actual research evidence and supporting sources."
    },
    {
      icon: Search,
      title: "Evidence Retrieval",
      description:
        "Discover relevant paragraphs across multiple research papers using intelligent search."
    }
  ];

  // --------------------------------------------------
  // NAVIGATION
  // --------------------------------------------------

  const openDashboard = () => {
    setPage("dashboard");
    setActiveTab("Overview");

    window.scrollTo({
      top: 0,
      behavior: "instant"
    });

    loadPapers();
  };

  const goHome = () => {
    setPage("home");

    window.scrollTo({
      top: 0,
      behavior: "instant"
    });
  };

  // --------------------------------------------------
  // PDF UPLOAD
  // --------------------------------------------------

  const handleFileUpload = async (event) => {
    const selectedFiles = Array.from(event.target.files || []);

    event.target.value = "";

    if (selectedFiles.length === 0) return;

    setUploadNotice(null);

    const validFiles = [];
    const invalidFiles = [];

    selectedFiles.forEach((file) => {
      const isPdf =
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf");

      if (!isPdf) {
        invalidFiles.push(`${file.name}: Only PDF files are allowed.`);
      } else if (file.size === 0) {
        invalidFiles.push(`${file.name}: The file is empty.`);
      } else if (file.size > MAX_FILE_SIZE) {
        invalidFiles.push(`${file.name}: Maximum file size is 20 MB.`);
      } else {
        validFiles.push(file);
      }
    });

    if (validFiles.length === 0) {
      setUploadNotice({
        type: "error",
        message: invalidFiles.join("\n")
      });
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();

      validFiles.forEach((file) => {
        formData.append("files", file);
      });

      const response = await fetch(`${API_BASE}/upload-pdf`, {
        method: "POST",
        body: formData
      });

      const data = await readResponse(response);

      if (!response.ok) {
        const detail = data.detail;

        if (typeof detail === "object" && detail !== null) {
          const failed = detail.failed_documents || [];

          const failureMessages = failed.map(
            (item) => `${item.filename}: ${item.error}`
          );

          throw new Error(
            [
              detail.message || "PDF upload failed.",
              ...failureMessages
            ].join("\n")
          );
        }

        throw new Error(
          typeof detail === "string"
            ? detail
            : "PDF upload failed."
        );
      }

      await loadPapers();

      const messages = [];

      if (data.processed_files > 0) {
        messages.push(
          `${data.processed_files} PDF(s) processed successfully.`
        );
      }

      if (data.duplicate_files > 0) {
        const duplicateNames = (
          data.duplicate_documents || []
        ).map((item) => item.filename);

        messages.push(
          `${data.duplicate_files} duplicate PDF(s) skipped: ${duplicateNames.join(", ")}.`
        );
      }

      if (data.failed_files > 0) {
        const failedNames = (
          data.failed_documents || []
        ).map((item) => `${item.filename}: ${item.error}`);

        messages.push(`Failed uploads:\n${failedNames.join("\n")}`);
      }

      if (invalidFiles.length > 0) {
        messages.push(`Files not uploaded:\n${invalidFiles.join("\n")}`);
      }

      setUploadNotice({
        type:
          data.failed_files > 0 || invalidFiles.length > 0
            ? "warning"
            : "success",
        message: messages.join("\n\n") || "Upload request completed."
      });

    } catch (error) {
      console.error("PDF upload error:", error);

      setUploadNotice({
        type: "error",
        message: error.message || "Could not upload PDFs."
      });

    } finally {
      setUploading(false);
    }
  };

  // --------------------------------------------------
  // DELETE DOCUMENT
  // --------------------------------------------------

  const removePaper = async (documentId, filename) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) return;

    setDeletingPaperId(documentId);
    setUploadNotice(null);

    try {
      const response = await fetch(
        `${API_BASE}/documents/${documentId}`,
        { method: "DELETE" }
      );

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not delete this document."
        );
      }

      setPapers((previous) =>
        previous.filter(
          (paper) => paper.document_id !== documentId
        )
      );

      setUploadNotice({
        type: data.file_deleted === false ? "warning" : "success",
        message:
          data.file_deleted === false
            ? "Document removed from the database, but its original PDF could not be deleted from disk."
            : `${filename} was deleted successfully.`
      });

    } catch (error) {
      console.error("Document deletion error:", error);

      setUploadNotice({
        type: "error",
        message: error.message || "Could not delete the document."
      });

    } finally {
      setDeletingPaperId(null);
    }
  };

  // --------------------------------------------------
  // SIDEBAR
  // --------------------------------------------------

  const sidebarItems = [
    { name: "Overview", icon: LayoutDashboard },
    { name: "My Papers", icon: Files },
    { name: "Ask AI", icon: MessageSquare },
    { name: "Compare Papers", icon: GitCompareArrows },
    { name: "Verify Claims", icon: ShieldCheck }
  ];

  // --------------------------------------------------
  // DASHBOARD
  // --------------------------------------------------

  if (page === "dashboard") {
    return (
      <div className="min-h-screen bg-[#080b14] text-white flex">

        {/* SIDEBAR */}
        <aside className="w-64 min-h-screen border-r border-white/10 bg-[#0c1020] p-6 hidden md:flex flex-col">

          <button
            onClick={goHome}
            className="flex items-center gap-3 mb-12 text-left"
          >
            <div className="bg-violet-600 p-2 rounded-xl">
              <BrainCircuit size={24} />
            </div>

            <span className="text-lg font-bold">
              ResearchLens
              <span className="text-violet-400"> AI</span>
            </span>
          </button>

          <p className="text-xs text-gray-500 uppercase tracking-widest mb-5">
            Workspace
          </p>

          <div className="space-y-2">
            {sidebarItems.map((item) => {
              const Icon = item.icon;

              return (
                <button
                  key={item.name}
                  onClick={() => setActiveTab(item.name)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition ${
                    activeTab === item.name
                      ? "bg-violet-600/20 text-violet-300 border border-violet-500/20"
                      : "text-gray-400 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  <Icon size={19} />
                  {item.name}
                </button>
              );
            })}
          </div>

          <div className="mt-auto border-t border-white/10 pt-6">
            <button
              onClick={goHome}
              className="flex items-center gap-3 text-gray-400 hover:text-white text-sm"
            >
              <Home size={18} />
              Back to Home
            </button>
          </div>
        </aside>

        {/* MAIN DASHBOARD */}
        <main className="flex-1 min-w-0">

          <header className="h-20 border-b border-white/10 flex items-center justify-between px-6 md:px-10">
            <div>
              <h1 className="text-xl font-semibold">{activeTab}</h1>
              <p className="text-gray-500 text-xs mt-1">
                Your intelligent research workspace
              </p>
            </div>

            <button
              onClick={goHome}
              className="text-sm text-gray-400 hover:text-white flex items-center gap-2"
            >
              <Home size={17} />
              <span className="hidden sm:inline">Home</span>
            </button>
          </header>

          {activeTab === "Ask AI" ? (
            <div className="w-full">
              <ResearchAssistant papers={papers} />
            </div>
          ) : (
            <div className="p-6 md:p-10 max-w-7xl mx-auto">

              {/* OVERVIEW */}
              {activeTab === "Overview" && (
                <>
                  <div className="mb-10">
                    <p className="text-violet-400 text-sm font-medium">
                      RESEARCH WORKSPACE
                    </p>

                    <h2 className="text-3xl md:text-4xl font-bold mt-3">
                      Welcome to ResearchLens.
                    </h2>

                    <p className="text-gray-400 mt-3">
                      Your research journey starts here. Upload papers,
                      explore evidence and discover insights.
                    </p>
                  </div>

                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">

                    <div className="bg-[#111729] border border-white/10 rounded-2xl p-6">
                      <div className="bg-violet-500/15 text-violet-400 p-3 rounded-xl w-fit">
                        <FileText size={24} />
                      </div>

                      <p className="text-gray-400 mt-6 text-sm">
                        Uploaded Papers
                      </p>

                      <h3 className="text-3xl font-bold mt-2">
                        {papers.length}
                      </h3>
                    </div>

                    <div className="bg-[#111729] border border-white/10 rounded-2xl p-6">
                      <div className="bg-blue-500/15 text-blue-400 p-3 rounded-xl w-fit">
                        <Search size={24} />
                      </div>

                      <p className="text-gray-400 mt-6 text-sm">
                        Research Queries
                      </p>

                      <h3 className="text-3xl font-bold mt-2">0</h3>
                    </div>

                    <div className="bg-[#111729] border border-white/10 rounded-2xl p-6">
                      <div className="bg-cyan-500/15 text-cyan-400 p-3 rounded-xl w-fit">
                        <ShieldCheck size={24} />
                      </div>

                      <p className="text-gray-400 mt-6 text-sm">
                        Claims Verified
                      </p>

                      <h3 className="text-3xl font-bold mt-2">0</h3>
                    </div>

                  </div>

                  <div className="mt-10">
                    <h3 className="text-xl font-semibold mb-5">
                      Get Started
                    </h3>

                    <div className="grid md:grid-cols-2 gap-5">

                      <button
                        onClick={() => setActiveTab("My Papers")}
                        className="text-left bg-gradient-to-br from-violet-600/20 to-blue-600/10 border border-violet-500/20 rounded-2xl p-7 hover:border-violet-400/50 transition"
                      >
                        <Upload className="text-violet-400" size={28} />

                        <h4 className="text-lg font-semibold mt-5">
                          Upload Research Papers
                        </h4>

                        <p className="text-gray-400 text-sm mt-2">
                          Add your scientific PDFs to your research workspace.
                        </p>

                        <span className="text-violet-400 text-sm mt-5 inline-flex items-center gap-2">
                          Upload papers <ArrowRight size={16} />
                        </span>
                      </button>

                      <button
                        onClick={() => setActiveTab("Ask AI")}
                        className="text-left bg-gradient-to-br from-blue-600/20 to-cyan-600/10 border border-blue-500/20 rounded-2xl p-7 hover:border-blue-400/50 transition"
                      >
                        <BrainCircuit className="text-blue-400" size={28} />

                        <h4 className="text-lg font-semibold mt-5">
                          Ask Research Questions
                        </h4>

                        <p className="text-gray-400 text-sm mt-2">
                          Explore research questions using scientific literature.
                        </p>

                        <span className="text-blue-400 text-sm mt-5 inline-flex items-center gap-2">
                          Explore AI assistant <ArrowRight size={16} />
                        </span>
                      </button>

                    </div>
                  </div>
                </>
              )}

              {/* MY PAPERS */}
              {activeTab === "My Papers" && (
                <div>

                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5 mb-8">
                    <div>
                      <h2 className="text-2xl font-bold">
                        My Research Papers
                      </h2>

                      <p className="text-gray-400 mt-2 text-sm">
                        Manage your uploaded scientific documents and explore extracted content.
                      </p>
                    </div>

                    <div className="flex items-center gap-3">

                      <button
                        onClick={loadPapers}
                        disabled={loadingPapers}
                        className="p-3 rounded-xl border border-white/10 text-gray-400 hover:text-white hover:bg-white/5 transition disabled:opacity-50"
                        title="Refresh documents"
                      >
                        <RefreshCw
                          size={18}
                          className={loadingPapers ? "animate-spin" : ""}
                        />
                      </button>

                      <label
                        className={`cursor-pointer bg-violet-600 hover:bg-violet-500 px-5 py-3 rounded-xl font-medium text-sm flex items-center gap-2 w-fit transition ${
                          uploading ? "opacity-60 pointer-events-none" : ""
                        }`}
                      >
                        {uploading ? (
                          <Loader2 size={18} className="animate-spin" />
                        ) : (
                          <Plus size={18} />
                        )}

                        {uploading ? "Uploading..." : "Upload PDFs"}

                        <input
                          type="file"
                          accept=".pdf,application/pdf"
                          multiple
                          onChange={handleFileUpload}
                          disabled={uploading}
                          className="hidden"
                        />
                      </label>
                    </div>
                  </div>

                  {/* UPLOAD STATUS */}
                  {uploadNotice && (
                    <div
                      className={`mb-6 p-4 rounded-xl border flex items-start gap-3 ${
                        uploadNotice.type === "success"
                          ? "bg-green-500/10 border-green-500/20 text-green-300"
                          : uploadNotice.type === "warning"
                            ? "bg-yellow-500/10 border-yellow-500/20 text-yellow-300"
                            : "bg-red-500/10 border-red-500/20 text-red-300"
                      }`}
                    >
                      {uploadNotice.type === "success" ? (
                        <CheckCircle2 size={20} className="shrink-0 mt-0.5" />
                      ) : (
                        <AlertCircle size={20} className="shrink-0 mt-0.5" />
                      )}

                      <p className="text-sm whitespace-pre-line">
                        {uploadNotice.message}
                      </p>
                    </div>
                  )}

                  {/* BACKEND CONNECTION ERROR */}
                  {paperError && (
                    <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 flex items-start gap-3">
                      <AlertCircle size={20} className="shrink-0 mt-0.5" />

                      <div>
                        <p className="text-sm font-medium">
                          Could not load your documents
                        </p>

                        <p className="text-sm mt-1 whitespace-pre-line">
                          {paperError}
                        </p>

                        <button
                          onClick={loadPapers}
                          className="text-sm underline mt-2"
                        >
                          Try again
                        </button>
                      </div>
                    </div>
                  )}

                  {/* UPLOAD AREA */}
                  <div className="border border-dashed border-white/20 bg-white/[0.02] rounded-2xl p-10 md:p-16 text-center">

                    <div className="bg-violet-500/15 text-violet-400 p-5 rounded-2xl w-fit mx-auto">
                      <Upload size={35} />
                    </div>

                    <h3 className="text-xl font-semibold mt-6">
                      Upload your research papers
                    </h3>

                    <p className="text-gray-400 text-sm mt-3">
                      Select one or multiple PDF files from your computer.
                    </p>

                    <p className="text-gray-500 text-xs mt-2">
                      Maximum file size: 20 MB per PDF
                    </p>

                    <label
                      className={`inline-flex mt-6 cursor-pointer bg-white text-black px-6 py-3 rounded-xl font-semibold text-sm hover:bg-violet-100 transition ${
                        uploading ? "opacity-60 pointer-events-none" : ""
                      }`}
                    >
                      {uploading ? "Uploading..." : "Browse Files"}

                      <input
                        type="file"
                        accept=".pdf,application/pdf"
                        multiple
                        onChange={handleFileUpload}
                        disabled={uploading}
                        className="hidden"
                      />
                    </label>

                  </div>

                  {/* DOCUMENT LIST */}
                  <div className="mt-8">

                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold">
                        Uploaded Documents ({papers.length})
                      </h3>

                      {loadingPapers && (
                        <span className="text-xs text-violet-400 flex items-center gap-2">
                          <Loader2 size={14} className="animate-spin" />
                          Loading...
                        </span>
                      )}
                    </div>

                    {loadingPapers && papers.length === 0 ? (
                      <div className="text-center py-10 text-gray-400">
                        <Loader2 className="animate-spin mx-auto mb-3" size={25} />
                        Loading your documents...
                      </div>
                    ) : papers.length === 0 ? (
                      <div className="text-center py-10 border border-white/10 rounded-xl bg-white/[0.02]">
                        <FileText size={30} className="mx-auto text-gray-600" />

                        <p className="text-gray-400 text-sm mt-3">
                          No papers uploaded yet.
                        </p>

                        <p className="text-gray-600 text-xs mt-1">
                          Your uploaded PDFs will appear here.
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-4">

                        {papers.map((paper) => (
                          <div
                            key={paper.document_id}
                            className="bg-[#111729] border border-white/10 rounded-xl p-5"
                          >

                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">

                              <div className="flex items-center gap-3 min-w-0">

                                <div className="bg-violet-500/15 p-3 rounded-xl shrink-0">
                                  <FileText className="text-violet-400" size={23} />
                                </div>

                                <div className="min-w-0">

                                  <p className="text-sm font-medium truncate">
                                    {paper.name}
                                  </p>

                                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500 mt-2">

                                    {paper.total_pages !== undefined && (
                                      <span>
                                        {paper.total_pages} pages
                                      </span>
                                    )}

                                    {paper.total_chunks !== undefined && (
                                      <span>
                                        {paper.total_chunks} chunks
                                      </span>
                                    )}

                                    {paper.size && (
                                      <span>
                                        {(paper.size / 1024 / 1024).toFixed(2)} MB
                                      </span>
                                    )}

                                  </div>

                                  {paper.uploaded_at && (
                                    <p className="text-xs text-gray-600 mt-1">
                                      Uploaded: {paper.uploaded_at}
                                    </p>
                                  )}

                                </div>
                              </div>

                              <div className="flex items-center gap-2 shrink-0">

                                <a
                                  href={`${API_BASE}/documents/${paper.document_id}/download`}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="text-gray-400 hover:text-violet-400 p-2 transition"
                                  title="Download original PDF"
                                >
                                  <Download size={18} />
                                </a>

                                <button
                                  onClick={() =>
                                    removePaper(paper.document_id, paper.name)
                                  }
                                  disabled={deletingPaperId === paper.document_id}
                                  className="text-gray-500 hover:text-red-400 p-2 disabled:opacity-50"
                                  title="Delete paper"
                                >
                                  {deletingPaperId === paper.document_id ? (
                                    <Loader2 size={18} className="animate-spin" />
                                  ) : (
                                    <Trash2 size={18} />
                                  )}
                                </button>

                              </div>
                            </div>

                            {/* NEW PAPER VIEWER */}
                            <PaperChunks documentId={paper.document_id} />

                          </div>
                        ))}

                      </div>
                    )}

                  </div>
                </div>
              )}

              {/* COMPARE PAPERS */}
              {activeTab === "Compare Papers" && (
                <div className="max-w-3xl">

                  <div className="bg-violet-500/15 text-violet-400 p-4 rounded-xl w-fit">
                    <GitCompareArrows size={30} />
                  </div>

                  <h2 className="text-3xl font-bold mt-6">
                    Compare Research Papers
                  </h2>

                  <p className="text-gray-400 mt-3">
                    Compare methodologies, findings, datasets and limitations
                    across multiple research papers.
                  </p>

                  <div className="mt-8 bg-[#111729] border border-white/10 rounded-2xl p-6">

                    <h3 className="font-semibold mb-3">
                      Your document collection
                    </h3>

                    <p className="text-gray-400 text-sm">
                      {papers.length} paper(s) available in your document collection.
                    </p>

                    <button
                      onClick={() => setActiveTab("My Papers")}
                      className="mt-5 text-violet-400 text-sm hover:text-violet-300"
                    >
                      Manage papers <ArrowRight className="inline ml-1" size={15} />
                    </button>

                  </div>

                  <p className="text-gray-500 text-sm mt-5">
                    Paper comparison will be connected to the research engine.
                  </p>

                </div>
              )}

              {/* VERIFY CLAIMS */}
              {activeTab === "Verify Claims" && (
                <div className="max-w-3xl">

                  <div className="bg-cyan-500/15 text-cyan-400 p-4 rounded-xl w-fit">
                    <ShieldCheck size={30} />
                  </div>

                  <h2 className="text-3xl font-bold mt-6">
                    Scientific Claim Verification
                  </h2>

                  <p className="text-gray-400 mt-3">
                    Check whether a scientific claim is supported by evidence
                    from your uploaded research papers.
                  </p>

                  <div className="mt-8 bg-[#111729] border border-white/10 rounded-2xl p-6">

                    <label className="text-sm text-gray-300">
                      Enter a scientific claim
                    </label>

                    <textarea
                      placeholder="Enter the claim you want to verify..."
                      className="w-full h-32 mt-3 bg-[#080b14] border border-white/10 rounded-xl p-4 text-white outline-none focus:border-cyan-500 resize-none"
                    />

                    <button
                      disabled
                      className="mt-4 bg-cyan-600/50 text-white/60 px-5 py-3 rounded-xl text-sm font-semibold cursor-not-allowed"
                    >
                      Verify Claim
                    </button>

                  </div>

                  <p className="text-gray-500 text-sm mt-5">
                    Claim verification will be connected to the research engine.
                  </p>

                </div>
              )}

            </div>
          )}

        </main>
      </div>
    );
  }

  // --------------------------------------------------
  // LANDING PAGE
  // --------------------------------------------------

  return (
    <div className="min-h-screen bg-[#080b14] text-white overflow-hidden">

      {/* NAVBAR */}
      <nav className="flex items-center justify-between px-8 md:px-16 py-6 border-b border-white/10">

        <button
          onClick={scrollToTop}
          className="flex items-center gap-3"
        >
          <div className="bg-violet-600 p-2 rounded-xl">
            <BrainCircuit size={25} />
          </div>

          <span className="text-xl font-bold tracking-tight">
            ResearchLens<span className="text-violet-400"> AI</span>
          </span>
        </button>

        <div className="hidden md:flex items-center gap-9 text-sm text-gray-400">

          <button
            onClick={() => scrollToSection("features")}
            className="hover:text-white transition"
          >
            Features
          </button>

          <button
            onClick={() => scrollToSection("how-it-works")}
            className="hover:text-white transition"
          >
            How it works
          </button>

          <button
            onClick={() => scrollToSection("about")}
            className="hover:text-white transition"
          >
            About
          </button>

        </div>

        <button
          onClick={openDashboard}
          className="bg-white text-black px-5 py-2.5 rounded-lg font-semibold text-sm hover:bg-violet-100 transition"
        >
          Get Started <ArrowRight size={15} className="inline ml-1" />
        </button>

      </nav>

      {/* HERO SECTION */}
      <section className="relative px-8 md:px-16 pt-28 pb-24 text-center">

        <div className="absolute w-96 h-96 bg-violet-600/20 blur-[140px] rounded-full top-10 left-1/2 -translate-x-1/2 pointer-events-none" />

        <div className="relative max-w-4xl mx-auto">

          <div className="inline-flex items-center gap-2 border border-violet-400/30 bg-violet-500/10 px-4 py-2 rounded-full text-violet-300 text-sm mb-8">
            <Sparkles size={15} />
            AI-powered scientific research
          </div>

          <h1 className="text-5xl md:text-7xl font-bold leading-tight tracking-tight">
            Research Smarter.
            <br />

            <span className="bg-gradient-to-r from-violet-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Discover Deeper.
            </span>
          </h1>

          <p className="text-gray-400 text-lg md:text-xl mt-7 max-w-2xl mx-auto leading-relaxed">
            Your intelligent research companion. Explore scientific
            literature, compare papers, verify claims and discover
            insights backed by real evidence.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4 mt-10">

            <button
              onClick={openDashboard}
              className="bg-violet-600 hover:bg-violet-500 px-7 py-4 rounded-xl font-semibold transition shadow-lg shadow-violet-600/20"
            >
              Start Researching <ArrowRight className="inline ml-2" size={18} />
            </button>

            <button
              onClick={() => scrollToSection("features")}
              className="border border-white/15 hover:bg-white/5 px-7 py-4 rounded-xl font-semibold transition"
            >
              Explore Features
            </button>

          </div>

          <div className="mt-16 flex flex-wrap justify-center gap-8 text-sm text-gray-500">

            <span className="flex items-center gap-2">
              <FileText size={16} /> Multi-PDF Analysis
            </span>

            <span className="flex items-center gap-2">
              <ShieldCheck size={16} /> Evidence-Based Answers
            </span>

            <span className="flex items-center gap-2">
              <Microscope size={16} /> Scientific Reasoning
            </span>

          </div>

        </div>
      </section>

      {/* FEATURES SECTION */}
      <section
        id="features"
        className="scroll-mt-6 px-8 md:px-16 py-24 bg-[#0c1020]"
      >

        <div className="max-w-6xl mx-auto">

          <div className="text-center mb-16">

            <p className="text-violet-400 text-sm font-semibold tracking-widest uppercase">
              Powerful Capabilities
            </p>

            <h2 className="text-4xl md:text-5xl font-bold mt-4">
              Everything Research Needs
            </h2>

            <p className="text-gray-400 mt-5 max-w-2xl mx-auto">
              Move beyond traditional paper searching.
              Let AI help you understand, compare and verify scientific knowledge.
            </p>

          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            {features.map((feature, index) => {
              const Icon = feature.icon;

              return (
                <div
                  key={index}
                  className="group border border-white/10 bg-white/[0.03] hover:bg-violet-500/[0.06] hover:border-violet-400/40 rounded-2xl p-8 transition duration-300"
                >

                  <div className="bg-violet-500/15 text-violet-400 p-3 rounded-xl w-fit mb-6">
                    <Icon size={27} />
                  </div>

                  <h3 className="text-xl font-semibold mb-3">
                    {feature.title}
                  </h3>

                  <p className="text-gray-400 leading-relaxed">
                    {feature.description}
                  </p>

                  <div className="mt-6 text-violet-400 text-sm font-medium">
                    Explore capability <ChevronRight className="inline" size={16} />
                  </div>

                </div>
              );
            })}

          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section
        id="how-it-works"
        className="scroll-mt-6 px-8 md:px-16 py-24"
      >

        <div className="max-w-5xl mx-auto text-center">

          <p className="text-violet-400 text-sm font-semibold tracking-widest uppercase">
            Simple Workflow
          </p>

          <h2 className="text-4xl md:text-5xl font-bold mt-4">
            From Papers to Insights
          </h2>

          <div className="grid md:grid-cols-3 gap-8 mt-16">

            {[
              {
                icon: Upload,
                title: "Upload Papers",
                description: "Upload your research PDFs to build your knowledge collection."
              },
              {
                icon: Search,
                title: "Explore Evidence",
                description: "Find relevant paragraphs and evidence across your papers."
              },
              {
                icon: Sparkles,
                title: "Discover Insights",
                description: "Get AI-powered answers, comparisons and claim verification."
              }
            ].map((step, index) => {
              const Icon = step.icon;

              return (
                <div key={index} className="text-center">

                  <div className="mx-auto bg-violet-500/15 text-violet-400 w-16 h-16 rounded-2xl flex items-center justify-center">
                    <Icon size={29} />
                  </div>

                  <p className="text-violet-400 text-sm mt-6">
                    STEP 0{index + 1}
                  </p>

                  <h3 className="text-xl font-semibold mt-2">
                    {step.title}
                  </h3>

                  <p className="text-gray-400 mt-3 leading-relaxed">
                    {step.description}
                  </p>

                </div>
              );
            })}

          </div>
        </div>
      </section>

      {/* CTA / ABOUT */}
      <section
        id="about"
        className="scroll-mt-6 px-8 md:px-16 pb-24"
      >

        <div className="max-w-5xl mx-auto text-center bg-gradient-to-br from-violet-600/20 to-blue-600/10 border border-violet-400/20 rounded-3xl p-12 md:p-16">

          <BookOpen size={40} className="mx-auto text-violet-400" />

          <h2 className="text-3xl md:text-5xl font-bold mt-6">
            Make Every Research Paper Count.
          </h2>

          <p className="text-gray-400 mt-5 max-w-xl mx-auto">
            Spend less time searching and more time discovering.
            Your next research breakthrough starts here.
          </p>

          <button
            onClick={openDashboard}
            className="mt-8 bg-white text-black px-7 py-4 rounded-xl font-semibold hover:bg-violet-100 transition"
          >
            Get Started <ArrowRight className="inline ml-2" size={18} />
          </button>

        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-white/10 px-8 md:px-16 py-8">

        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">

          <div className="font-bold text-lg">
            ResearchLens<span className="text-violet-400"> AI</span>
          </div>

          <p className="text-gray-500 text-sm">
            Intelligent Research. Evidence-Based Discovery.
          </p>

          <p className="text-gray-600 text-sm">
            © 2026 ResearchLens AI
          </p>

        </div>
      </footer>

      {/* BACK TO TOP BUTTON */}
      <button
        onClick={scrollToTop}
        aria-label="Back to top"
        title="Back to top"
        className={`fixed bottom-7 right-7 z-50 flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-4 py-3 rounded-full shadow-lg shadow-violet-600/30 transition-all duration-300 ${
          showBackToTop
            ? "opacity-100 translate-y-0 pointer-events-auto"
            : "opacity-0 translate-y-5 pointer-events-none"
        }`}
      >
        <ArrowUp size={19} />
        <span className="text-sm font-semibold">Back to Top</span>
      </button>

    </div>
  );
}

export default App;
