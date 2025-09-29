import Navbar from "../components/Navbar";
import "../styles/Home.scss";

export default function Home() {
  return (
    <>
      <Navbar />
      <div className="home-container">
        <h1>Welcome to Bragboard</h1>
        <p>Your dashboard for achievements, projects, and moore!</p>
      </div>
    </>
  );
}
