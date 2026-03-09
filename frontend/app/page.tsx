import Link from "next/link";

const features = [
  {
    icon: "🤖",
    title: "AI Chat",
    description: "Built-in LLM abstraction layer with OpenAI & Anthropic support. Usage tracking included.",
  },
  {
    icon: "🏢",
    title: "Multi-tenancy",
    description: "Row-level tenant isolation out of the box. Role-based access with owner, admin, member.",
  },
  {
    icon: "💳",
    title: "Stripe Billing",
    description: "Subscription management with webhooks, portal sessions, and plan upgrades.",
  },
  {
    icon: "🛡️",
    title: "GDPR Compliance",
    description: "Data export, deletion, and audit log anonymization. Privacy-first architecture.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-950">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <span className="text-xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
          AI SaaS Starter
        </span>
        <div className="flex gap-3">
          <Link
            href="/login"
            className="px-4 py-2 text-sm text-gray-300 hover:text-white transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="px-4 py-2 text-sm rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 hover:opacity-90 transition-opacity"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="flex flex-col items-center text-center px-6 pt-24 pb-20 max-w-4xl mx-auto">
        <h1 className="text-5xl sm:text-6xl font-extrabold leading-tight tracking-tight">
          <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Build AI Products
          </span>
          <br />
          Faster
        </h1>
        <p className="mt-6 text-lg text-gray-400 max-w-2xl">
          Production-ready SaaS boilerplate with FastAPI, Next.js, built-in AI module, Stripe
          billing, JWT auth, and GDPR compliance. Ship your AI product in days, not months.
        </p>
        <div className="mt-10 flex gap-4">
          <Link
            href="/register"
            className="px-8 py-3 rounded-xl font-semibold bg-gradient-to-r from-violet-600 to-indigo-600 hover:opacity-90 transition-opacity shadow-lg shadow-violet-500/25"
          >
            Get Started Free
          </Link>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-3 rounded-xl font-semibold border border-gray-700 text-gray-300 hover:border-gray-500 hover:text-white transition-colors"
          >
            View on GitHub
          </a>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 pb-24 max-w-6xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="bg-gray-900 border border-gray-800 rounded-2xl p-6 hover:border-gray-700 transition-colors"
            >
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 text-center text-sm text-gray-500">
        &copy; 2026 ForwardCodeSolutions
      </footer>
    </div>
  );
}
