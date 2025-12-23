"use client";
import { useEffect, useState } from "react";

import First from "./first/page";
import Auth from "./auth/page";

export default function Home() {
  const [isAuth, setIsAuth] = useState(null);

  useEffect(() => {
    const storedAuth = localStorage.getItem("isAuth");
    setIsAuth(storedAuth === "true");

    const handleStorageChange = () => {
      const auth = localStorage.getItem("isAuth");
      setIsAuth(auth === "true");
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  if (isAuth === null) return null;

  return <>{isAuth ? <First /> : <Auth />}</>;
}
