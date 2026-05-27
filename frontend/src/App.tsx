import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { AppLayout } from '@/components/layout/AppLayout'
import { ExperimentPage } from '@/pages/ExperimentPage'
import { HomePage } from '@/pages/HomePage'
import { NewExperimentPage } from '@/pages/NewExperimentPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />} path="/">
          <Route element={<HomePage />} index />
          <Route element={<NewExperimentPage />} path="experiments/new" />
          <Route element={<ExperimentPage />} path="experiments/:id" />
        </Route>
        <Route element={<Navigate replace to="/" />} path="*" />
      </Routes>
    </BrowserRouter>
  )
}
