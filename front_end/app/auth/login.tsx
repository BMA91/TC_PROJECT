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

  const handleChange = (e: any) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (e: any) => {
    e.preventDefault();
    console.log(formDataLog); //lhna nbackendi

    if (formDataLog.address === "" || formDataLog.password === "") {
      alert("enter your information");
      return;
    }

    setLoginData(formDataLog); 
    router.push("/dashboard"); 
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
          className="bg-[#091636] text-white h-10 rounded-2xl"
        >
          Se connecter
        </button>
      </form>
    </>
  );
}
