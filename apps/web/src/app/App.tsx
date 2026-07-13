import { Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { LandingPage } from "@/features/landing/LandingPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { ChatPage } from "@/features/chat/ChatPage";
import { RecommendationsPage } from "@/features/recommendations/RecommendationsPage";
import { ProposalGeneratorPage } from "@/features/proposals/ProposalGeneratorPage";
import { ProfilePage } from "@/features/profile/ProfilePage";
import { HistoryPage } from "@/features/history/HistoryPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />

      <Route element={<AppShell />}>
        <Route path="/app" element={<DashboardPage />} />
        <Route path="/app/chat" element={<ChatPage />} />
        <Route path="/app/recommendations" element={<RecommendationsPage />} />
        <Route path="/app/proposals" element={<ProposalGeneratorPage />} />
        <Route path="/app/profile" element={<ProfilePage />} />
        <Route path="/app/history" element={<HistoryPage />} />
      </Route>
    </Routes>
  );
}

