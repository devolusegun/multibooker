import React from 'react';

const Login = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h2 className="text-2xl font-semibold mb-6 text-center">Login</h2>
        <form>
          <input type="email" placeholder="Email" className="input mb-4" />
          <input type="password" placeholder="Password" className="input mb-4" />
          <button type="submit" className="btn-primary w-full">Log In</button>
        </form>
        <p className="text-sm text-center mt-4">
          Don’t have an account? <a href="/register" className="text-blue-500">Register</a>
        </p>
      </div>
    </div>
  );
};

export default Login;