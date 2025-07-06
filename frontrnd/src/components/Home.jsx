import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6">
      <h1 className="text-3xl font-bold">Resume Skill Matcher</h1>
      <div className="flex gap-4 flex-wrap justify-center">
        <Link
          to="/predict"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Predict
        </Link>
        <Link
          to="/retrain"
          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
        >
          Retrain
        </Link>
        <Link
          to="/analyze"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Analyze
        </Link>
        <Link
          to="/resumes"
          className="bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700"
        >
          View Resumes
        </Link>
        <Link
          to="/roles"
          className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
        >
          Manage Roles
        </Link>
      </div>
    </div>
  );
};

export default Home;
