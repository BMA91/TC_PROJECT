"use client";
import { useState } from "react";
import "./page.css";
import Link from "next/link";
const logo = "/images/logo.svg";
const back = "/images/back.svg";
export default function First() {
  return (
    <>
      <section className="first">
        <img src={back} className="back" />
        <div className="ml-auto bg-[#0C2155] h-10 "></div>
        <nav className="bg-transparent ">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center  ">
              <div className="flex items-center gap-2 pl">
                <div className="flex gap-1">
                  <img src={logo} />
                </div>
                <span className="text-2xl font-bold text-blue-900">Doxa</span>
              </div>

              <div className="flex gap-8 ml-24">
                <a
                  href="/dashboard"
                  className="text-blue-900 font-medium hover:text-blue-700 transition"
                >
                  Home
                </a>
                <a
                  href="#"
                  className="text-blue-900 font-medium hover:text-blue-700 transition"
                >
                  À propos
                </a>
                <a
                  href="#"
                  className="text-blue-900 font-medium hover:text-blue-700 transition"
                >
                  Tarification
                </a>
                <a
                  href="#"
                  className="text-blue-900 font-medium hover:text-blue-700 transition"
                >
                  Aide
                </a>
              </div>

              <Link
                href="/auth"
                className="ml-auto bg-blue-600 px-6 py-2 hover:bg-blue-700 text-white font-medium rounded-lg transition shadow-md"
              >
                Vos tickets
              </Link>
            </div>
          </div>
        </nav>
        <div className="first-body flex flex-col justify-center items-center h-100">
          <div className="flex flex-col justify-center items-center gap-4">
            <p className="main-tit font-bold">
              Ensemble, chaque projet <br /> devient plus simple.
            </p>
            <p>
              Doxa, est une entreprise technologique, proposant une solution
              SaaS de gestion de projets collaboratifs.
            </p>
          </div>
          <div className="flex flex-row items-center justify-center  gap-7 p-6 w-110">
            <div className="input-container">
              <div className="input-wrapper">
                <input
                  type="email"
                  className="email-input"
                  placeholder="Enter your email"
                />
                <Link href="/auth" className="login-button">
                  log in
                </Link>
              </div>
            </div>

            <Link
              href="/auth"
              className="bg-[#091636] flex items-center justify-center text-white h-15 px-12 rounded-2xl whitespace-nowrap"
            >
              Créer un compte
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
