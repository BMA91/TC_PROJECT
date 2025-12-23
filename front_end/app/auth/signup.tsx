"use client";
import { useState, useContext } from "react";
import { useRouter } from "next/navigation";
import { LoginContext } from "../layout";

export default function SignUp() {
  const context = useContext(LoginContext);
  if (!context) throw new Error("LoginContext is not available");

  const { setLoginData } = context;
  const router = useRouter();
  const [formData, setFormData1] = useState({
    nom: "",
    prenom: "",
    email: "",
    telephone: "",
    password: "",
    confirmPassword: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e: any) => {
    const { name, value } = e.target;
    setFormData1((prev) => ({
      ...prev,
      [name]: value,
    }));
    
    if (error) setError("");
    if (success) setSuccess("");
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setError("");
    setSuccess("");

  
    if (!formData.nom || !formData.prenom || !formData.email || !formData.telephone || !formData.password || !formData.confirmPassword) {
      setError("Veuillez remplir tous les champs");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Les mots de passe ne correspondent pas");
      return;
    }

    if (formData.password.length < 4) {
      setError("Le mot de passe doit contenir au moins 4 caractères");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("/api/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          nom: formData.nom,
          prenom: formData.prenom,
          email: formData.email,
          telephone: formData.telephone,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Erreur lors de la création du compte");
        setIsLoading(false);
        return;
      }

  
      localStorage.setItem("isAuth", "true");
      if (data.user) {
        setLoginData(data.user);
        localStorage.setItem("userData", JSON.stringify(data.user));
      }

   
      router.push("/dashboard");
    } catch (err) {
      console.error("Signup error:", err);
      setError("Erreur de connexion au serveur. Veuillez réessayer.");
      setIsLoading(false);
    }
  };
  return (
    <>
      <form className="flex flex-col pb-6 pt-0 h-3/4" onSubmit={handleSubmit}>
        <div className="flex flex-row w-full mb-4 gap-2">
          <input
            type="text"
            name="nom"
            placeholder="Nom"
            value={formData.nom}
            onChange={handleChange}
            className="w-1/2 mt-5 p-2 rounded-lg"
          />

          <input
            type="text"
            name="prenom"
            placeholder="Prénom"
            value={formData.prenom}
            onChange={handleChange}
            className="w-1/2 mt-5 p-2 rounded-lg"
          />
        </div>

        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          className="rounded-lg h-10 p-2"
        />

        <input
          type="number"
          name="telephone"
          placeholder="Téléphone"
          value={formData.telephone}
          onChange={handleChange}
          className="mt-5 rounded-lg h-10 p-2"
        />

        <input
          type="password"
          name="password"
          placeholder="Mot de passe"
          value={formData.password}
          onChange={handleChange}
          className="mt-5 rounded-lg h-10 p-2"
        />

        <input
          type="password"
          name="confirmPassword"
          placeholder="Confirmer le mot de passe"
          value={formData.confirmPassword}
          onChange={handleChange}
          className="mt-5 rounded-lg h-10 p-2"
        />

        {error && (
          <div className="text-red-500 text-sm mt-2 mb-2 p-2 bg-red-50 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="text-green-500 text-sm mt-2 mb-2 p-2 bg-green-50 rounded">
            {success}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="sub bg-[#091636] text-white h-10 rounded-2xl mt-5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? "Création du compte..." : "S'inscrire"}
        </button>
      </form>
    </>
  );
}
