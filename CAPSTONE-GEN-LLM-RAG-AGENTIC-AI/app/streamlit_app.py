from pathlib import Path
import sys

import streamlit as st

try:
    from app.ingestion import load_text, chunk_text
    from app.ollama_client import OllamaClient
    from app.orchestrator import RAGOrchestrator
    from app.auth import SimpleAuth
    from app.chat_history import ChatHistory
    from app.upload_service import UploadService
    from app.config import load_settings
    from app.store_factory import create_store
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from app.ingestion import load_text, chunk_text
    from app.ollama_client import OllamaClient
    from app.orchestrator import RAGOrchestrator
    from app.auth import SimpleAuth
    from app.chat_history import ChatHistory
    from app.upload_service import UploadService
    from app.config import load_settings
    from app.store_factory import create_store

settings = load_settings()


def _safe_rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
        return
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

st.set_page_config(page_title="Enterprise Document QA", layout="wide")
st.title("Enterprise Document QA with Local LLM + RAG")
st.caption("Production-ready local stack for AWS EC2")

store = create_store(settings)
ollama_client = OllamaClient(
    base_url=settings.ollama_base_url,
    request_timeout_seconds=settings.ollama_request_timeout_seconds,
    num_predict=settings.ollama_num_predict,
    keep_alive=settings.ollama_keep_alive,
)
if not ollama_client.is_available():
    st.error(
        f"Ollama is required but unavailable at {settings.ollama_base_url}. "
        "Start Ollama before launching the UI."
    )
    st.stop()
if not ollama_client.is_model_available(settings.ollama_model):
    st.error(
        f"Required Ollama model '{settings.ollama_model}' is not installed. "
        f"Run: ollama pull {settings.ollama_model}"
    )
    st.stop()
orchestrator = RAGOrchestrator(
    store,
    ollama_client,
    ollama_model=settings.ollama_model,
    top_k=settings.rag_top_k,
    max_context_words=settings.rag_max_context_words,
)
auth = SimpleAuth(users_file=settings.auth_users_file)
history = ChatHistory(history_file=settings.chat_history_file)
upload_service = UploadService(storage_dir=settings.upload_dir)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_notice" not in st.session_state:
    st.session_state.login_notice = ""

if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if auth.authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.login_notice = "Login successful"
            _safe_rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

if st.session_state.login_notice:
    st.success(st.session_state.login_notice)
    st.session_state.login_notice = ""

st.sidebar.header("Workspace")
st.sidebar.write("Authenticated user")
st.sidebar.caption(f"Vector backend: {settings.vector_backend}")
st.sidebar.success(f"Ollama: connected ({settings.ollama_model})")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    _safe_rerun()

uploaded_file = st.file_uploader(
    "Upload a document",
    type=["pdf", "txt", "md", "json", "yaml", "yml", "xml", "csv", "xlsx", "xls"],
    accept_multiple_files=False,
)

if st.button("Upload and index") and uploaded_file is not None:
    saved_path = upload_service.save_upload(uploaded_file, uploaded_file.name)
    text = load_text(saved_path)
    chunks = chunk_text(text)
    for chunk in chunks:
        store.add(chunk, source=uploaded_file.name)
    st.success(f"Indexed {len(chunks)} chunks from {uploaded_file.name}")

query = st.text_area("Ask a question about your documents")

if st.button("Run RAG") and query:
    try:
        with st.spinner("Generating answer with Ollama..."):
            result = orchestrator.run(query)
    except RuntimeError as exc:
        st.error(str(exc))
        st.info(
            "If this happens repeatedly, verify Ollama is running and increase "
            "OLLAMA_REQUEST_TIMEOUT_SECONDS in your environment."
        )
        st.stop()

    st.subheader("Answer")
    st.markdown(f"> {result['answer']}")

    st.subheader("Retrieved Context")
    retrieval_results = result.get("retrieval_results", [])
    if retrieval_results:
        st.caption(f"Top matches: {len(retrieval_results)}")
        for index, item in enumerate(retrieval_results, start=1):
            source = item.get("source", "unknown")
            score = float(item.get("score", 0.0))
            chunk = item.get("chunk", "")
            with st.expander(f"Match {index} | Source: {source} | Score: {score:.3f}", expanded=(index == 1)):
                st.write(chunk)
    else:
        st.info("No relevant context retrieved.")

    st.subheader("Sources")
    sources = result.get("sources", [])
    if sources:
        for source in sources:
            st.markdown(f"- {source}")
    else:
        st.write("No sources available")
    history.add(query, result["answer"])

st.subheader("Chat history")
for item in reversed(history.load()):
    with st.container(border=True):
        st.markdown(f"**Q:** {item['question']}")
        st.markdown(f"**A:** {item['answer']}")
