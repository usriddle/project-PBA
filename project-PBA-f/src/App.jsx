import { BrowserRouter, Route, Routes } from "react-router";
import MainPage from './pages/mainPage';
import './App.css'

function App() {
  return (
    <BrowserRouter>
    <Routes>
      <Route index element={<MainPage/>}/>
    </Routes>
    </BrowserRouter>
  )
}

export default App
