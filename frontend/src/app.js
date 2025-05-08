import React from "react";
import {BrowserRouter, Routes, Route} from "react-router-dom"
import Main from "./pages/MainPage/mainPage";
import Search from "./pages/SearchPage/searchPage";

function App(){
    return(
        <BrowserRouter>
            <Routes>
                <Route element={<Main/>} path="/Main"></Route>
                <Route element={<Search/>} path="/Search"></Route>
            </Routes>
        </BrowserRouter>
    )
}
export default App;