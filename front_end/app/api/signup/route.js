import { NextResponse } from 'next/server';

// Backend API URL - adjust if your backend runs on a different port
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request) {
  try {
    const body = await request.json();
    const { nom, prenom, email, telephone, password } = body;

    // Validate input
    if (!nom || !prenom || !email || !telephone || !password) {
      return NextResponse.json(
        { error: 'Tous les champs sont requis' },
        { status: 400 }
      );
    }

    // Call backend API to create user
    const response = await fetch(`${BACKEND_URL}/users/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        nom,
        prenom,
        email,
        telephone,
        password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      // Backend returned an error
      return NextResponse.json(
        { error: data.detail || 'Erreur lors de la création du compte' },
        { status: response.status }
      );
    }

    // Success - return user data
    return NextResponse.json(
      { 
        success: true, 
        user: data,
        message: 'Compte créé avec succès'
      },
      { status: 201 }
    );
  } catch (error) {
    console.error('Signup API error:', error);
    return NextResponse.json(
      { error: 'Échec de la connexion au serveur. Veuillez réessayer.' },
      { status: 500 }
    );
  }
}

