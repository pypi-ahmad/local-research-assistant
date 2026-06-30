import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "../components/Layout";
import { ChatPage } from "../pages/ChatPage";
import { DashboardPage } from "../pages/DashboardPage";
import { DocumentsPage } from "../pages/DocumentsPage";
import { FlashcardsPage } from "../pages/FlashcardsPage";
import { KnowledgeBasePage } from "../pages/KnowledgeBasePage";
import { KnowledgeGraphPage } from "../pages/KnowledgeGraphPage";
import { ModelManagerPage } from "../pages/ModelManagerPage";
import { MonitoringPage } from "../pages/MonitoringPage";
import { NotebooksPage } from "../pages/NotebooksPage";
import { OcrPage } from "../pages/OcrPage";
import { QuizzesPage } from "../pages/QuizzesPage";
import { SearchPage } from "../pages/SearchPage";
import { SettingsPage } from "../pages/SettingsPage";
import { StudyToolsPage } from "../pages/StudyToolsPage";
import { WorkspacePage } from "../pages/WorkspacePage";
import { LoginPage } from "../pages/LoginPage";
import { useAuthStore } from "../stores/auth";

function ProtectedLayout() {
  const token = useAuthStore((state) => state.token);
  return token ? <Layout /> : <Navigate to="/login" replace />;
}

export function AppRouter() {
  return (
    <Routes>
      <Route element={<LoginPage />} path="/login" />
      <Route element={<ProtectedLayout />} path="/">
        <Route element={<DashboardPage />} index />
        <Route element={<WorkspacePage />} path="workspace" />
        <Route element={<ChatPage />} path="chat" />
        <Route element={<DocumentsPage />} path="documents" />
        <Route element={<KnowledgeBasePage />} path="knowledge-base" />
        <Route element={<SearchPage />} path="search" />
        <Route element={<OcrPage />} path="ocr" />
        <Route element={<NotebooksPage />} path="notebooks" />
        <Route element={<KnowledgeGraphPage />} path="knowledge-graph" />
        <Route element={<StudyToolsPage />} path="study-tools" />
        <Route element={<FlashcardsPage />} path="flashcards" />
        <Route element={<QuizzesPage />} path="quizzes" />
        <Route element={<SettingsPage />} path="settings" />
        <Route element={<ModelManagerPage />} path="model-manager" />
        <Route element={<MonitoringPage />} path="monitoring" />
      </Route>
      <Route element={<Navigate to="/login" replace />} path="*" />
    </Routes>
  );
}
