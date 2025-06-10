// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBcpx5gOGxxD1Q9hGZyoz_UA6ZDNB2NkVk",
  authDomain: "vokaflow-c1061.firebaseapp.com",
  projectId: "vokaflow-c1061",
  storageBucket: "vokaflow-c1061.firebasestorage.app",
  messagingSenderId: "991486137413",
  appId: "1:991486137413:web:439184a670885a5dbdbf2c",
  measurementId: "G-GKDHZB0CND"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);
const db = getFirestore(app);

export { auth, db, analytics };
