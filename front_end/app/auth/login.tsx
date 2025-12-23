"use client";
import { useState, useContext } from "react";
import { useRouter } from "next/navigation";
import { LoginContext } from "../layout";

export default function Login() {
  const context = useContext(LoginContext);
  if (!context) throw new Error("LoginContext is not available");

  const { setLoginData } = context;
  const router = useRouter();

  const [formDataLog, setFormData] = useState({
    address: "",
    password: "",
    remember: false,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e: any) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));

    if (error) setError("");
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setError("");

    if (formDataLog.address === "" || formDataLog.password === "") {
      setError("Veuillez entrer vos informations");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          address: formDataLog.address,
          password: formDataLog.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Email ou mot de passe invalide");
        setIsLoading(false);
        return;
      }

      if (data.user) {
        setLoginData(data.user);
        localStorage.setItem("isAuth", "true");
        localStorage.setItem("userData", JSON.stringify(data.user));
        window.dispatchEvent(new Event("storage"));
      }

      router.push("/dashboard");
    } catch (err) {
      console.error("Login error:", err);
      setError("Erreur de connexion au serveur. Veuillez réessayer.");
      setIsLoading(false);
    }
  };

  return (
    <>
      <form className="flex flex-col h-3/4" onSubmit={handleSubmit}>
        <div className="flex flex-col w-full mb-4 gap-2">
          <h1>
            <b>Connection a Doxa</b>
          </h1>
          <p>votre espace de projet collaboratif</p>
        </div>

        <input
          type="email"
          placeholder="Email"
          name="address"
          className="rounded-lg h-10 p-2"
          value={formDataLog.address}
          onChange={handleChange}
        />

        <input
          type="password"
          name="password"
          placeholder="Mot de passe"
          className="mt-5 mb-5 rounded-lg h-10 p-2"
          value={formDataLog.password}
          onChange={handleChange}
        />

        {error && (
          <div className="text-red-500 text-sm mb-2 p-2 bg-red-50 rounded">
            {error}
          </div>
        )}

        <div className="pb-2">
          <input
            type="checkbox"
            name="remember"
            className="rem"
            checked={formDataLog.remember}
            onChange={handleChange}
          />
          remembre me
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="bg-[#091636] text-white h-10 rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? "Connexion..." : "Se connecter"}
        </button>
      </form>
    </>
  );
}
