import { BrowserRouter, Routes, Route } from 'react-router-dom'
import TopNav from './components/TopNav'
import Dashboard from './pages/Dashboard'
import NuevoIndicador from './pages/NuevoIndicador'
import ActualizarIndicador from './pages/ActualizarIndicador'
import GanttPage from './pages/GanttPage'
import HistorialPage from './pages/HistorialPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<TopNav />}>
          <Route index element={<Dashboard />} />
          <Route path="nuevo" element={<NuevoIndicador />} />
          <Route path="actualizar" element={<ActualizarIndicador />} />
          <Route path="gantt" element={<GanttPage />} />
          <Route path="historial" element={<HistorialPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
