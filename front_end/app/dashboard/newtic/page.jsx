"use client";

import { useState, useContext, useEffect } from "react";
import { useRouter } from "next/navigation";
import { LoginContext } from "../../layout";
import Link from "next/link";
import Image from "next/image";

const ticketTypes = [
  {
    label: "L'application ne se charge pas.",
    value: "L'application ne se charge pas.",
  },
  { label: "Plateforme inaccessible", value: "Plateforme inaccessible" },
  {
    label: "Un problème de synchronisation bancaire",
    value: "Un problème de synchronisation bancaire",
  },
  { label: "Erreur système", value: "Erreur système" },
  { label: "Blocage total d'un projet", value: "Blocage total d'un projet" },
];

const logo = "/images/logo.svg";
const userp = "/images/user.svg";

export default function TicketsPage() {
  const context = useContext(LoginContext);
  const { loginData } = context ?? {};

  const router = useRouter();

  const [menu, setMenu] = useState(false);
  const [formData, setFormData] = useState({
    ticketType: "",
    subject: "",
    description: "",
    attachment: null,
  });

  useEffect(() => {
    if (!loginData) {
      router.push("/auth");
    }
  }, [loginData, router]);

  if (!context) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setFormData((prev) => ({ ...prev, attachment: e.target.files[0] }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(formData); // lhna tbackendi
  };

  return (
    <main>
      <div className="bg-[#0C2155] h-10 w-full"></div>

      <nav className="px-6 py-4 flex items-center">
        <div className="flex items-center gap-2">
          <Image src={logo} alt="Doxa logo" width={32} height={32} />
          <span className="text-2xl font-bold text-blue-900">Doxa</span>
        </div>

        <div className="flex gap-8 ml-24">
          <a href="/dashboard" className="text-blue-900 font-medium">
            Home
          </a>
          <a className="text-blue-900 font-medium">À propos</a>
          <a className="text-blue-900 font-medium">Tarification</a>
          <a className="text-blue-900 font-medium">Aide</a>
        </div>

        <Link
          href="/dashboard/tickets"
          className="ml-auto bg-blue-600 px-6 py-2 text-white rounded-lg hover:bg-blue-700"
        >
          Vos tickets
        </Link>

        <div className="relative pl-6">
          <button
            onClick={() => setMenu(!menu)}
            className="flex items-center gap-2"
          >
            <Image src={userp} alt="Profile" width={32} height={32} />
            Profile
          </button>

          {menu && (
            <div className="absolute right-0 mt-3 w-56 bg-[#0C2155] text-white p-4 rounded-xl">
              <p className="font-semibold">{loginData?.address ?? "User"}</p>
              <p className="text-[#AAC7FF] text-sm">UI/UX Designer</p>

              <hr className="my-3 border-white/30" />

              <button className="border border-white rounded px-2 py-1 mb-3">
                Modify
              </button>

              <hr className="my-3 border-white/30" />

              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <img src="./s" alt="" />
                  <button>Notifications</button>
                </div>

                <div className="flex items-center gap-2">
                  <img src="./s" alt="" />
                  <button>Messages</button>
                </div>

                <hr className="my-2 border-white/30" />

                <div className="flex items-center gap-2">
                  <img src="./s" alt="" />
                  <button>Aide</button>
                </div>

                <div className="flex items-center gap-2">
                  <img src="./s" alt="" />
                  <button>Paramètres</button>
                </div>

                <hr className="my-2 border-white/30" />

                <button className="text-red-400 text-left">Logout</button>
              </div>
            </div>
          )}
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-8 py-14">
        <h1 className="text-3xl font-bold text-[#1E1E4B] mb-10">
          Demander à Doxa
        </h1>

        <form onSubmit={handleSubmit} className="space-y-8">
          <fieldset className="space-y-3">
            <legend className="font-medium mb-2">Type de ticket</legend>

            {ticketTypes.map((type) => (
              <label key={type.value} className="flex items-center gap-3">
                <input
                  type="radio"
                  name="ticketType"
                  value={type.value}
                  checked={formData.ticketType === type.value}
                  onChange={handleChange}
                  required
                />
                {type.label}
              </label>
            ))}
          </fieldset>

          <input
            name="subject"
            value={formData.subject}
            onChange={handleChange}
            placeholder="Sujet"
            className="w-full border rounded px-4 py-2"
          />

          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={4}
            className="w-full border rounded px-4 py-2"
          />

          <input type="file" onChange={handleFileChange} />

          <button
            className="bg-blue-600 text-white px-10 py-2 rounded-lg"
            onClick={() => {
             
            }}
          >
            Soumettre
          </button>
        </form>
      </div>
    </main>
  );
}
