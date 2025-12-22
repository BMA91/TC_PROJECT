"use client";
import { useState } from "react";
export default function SignUp() {
  const [formData, setFormData1] = useState({
    nom: "",
    prenom: "",
    email: "",
    telephone: "",
    password: "",
    confirmPassword: "",
  });
  const handleChange = (e: any) => {
    const { name, value } = e.target;
    setFormData1((prev) => ({
      ...prev,
      [name]: value,
    }));
  };
  const handleSubmit = (e: any) => {
    e.preventDefault();
    console.log(formData);
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
          className="mt-5 mb-5 rounded-lg h-10 p-2"
        />

        <button
          type="submit"
          className="sub bg-[#091636] text-white h-10 rounded-2xl"
        >
          Sign Up
        </button>
      </form>
    </>
  );
}
