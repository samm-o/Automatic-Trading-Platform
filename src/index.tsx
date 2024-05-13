import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import { ChakraProvider } from "@chakra-ui/react";
import Login from "./Login";
import Home from "./Home";
import StrategiesHome from "./StrategiesHome";
import OrdersHome from "./OrdersHome";

function App(): JSX.Element {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return !((localStorage.getItem("isLoggedIn") ?? "") === "");
  });

  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/login");
    }
  }, [navigate, isLoggedIn]);

  const handleLogout = (): void => {
    setIsLoggedIn(false);
    localStorage.removeItem("isLoggedIn");
  };

  return (
    <ChakraProvider>
      <Routes>
        <Route
          path="/login"
          element={
            <Login
              onLogin={() => {
                setIsLoggedIn(true);
                localStorage.setItem("isLoggedIn", "true");
              }}
            />
          }
        />
        <Route path="/" element={<Home onLogout={handleLogout} />} />
        <Route
          path="/stock/:symbol"
          element={<Home onLogout={handleLogout} />}
        />
        <Route
          path="/strategies"
          element={<StrategiesHome onLogout={handleLogout} />}
        />
        <Route
          path="/trades"
          element={<OrdersHome onLogout={handleLogout} />}
        />
      </Routes>
    </ChakraProvider>
  );
}

const rootElement = document.getElementById("root");

if (rootElement === null) {
  throw new Error("No element with id 'root' found");
}

// eslint-disable-next-line react/no-deprecated
ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
  rootElement,
);
