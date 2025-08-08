import React from 'react';
import { Brain, Zap, Shield, TrendingUp, Users, Code, Lightbulb } from 'lucide-react';

const AboutPage = () => {
  const features = [
    {
      icon: <Brain className="h-8 w-8 text-primary-600" />,
      title: 'AI-Powered Matching',
      description: 'Uses OpenAI embeddings to semantically match products across different platforms, even when product names vary.'
    },
    {
      icon: <Zap className="h-8 w-8 text-yellow-600" />,
      title: 'Lightning Fast',
      description: 'Concurrent scraping and optimized algorithms ensure you get results in seconds, not minutes.'
    },
    {
      icon: <Shield className="h-8 w-8 text-green-600" />,
      title: 'Real-time Data',
      description: 'Fresh price data scraped in real-time from multiple e-commerce platforms for accurate comparisons.'
    },
    {
      icon: <TrendingUp className="h-8 w-8 text-blue-600" />,
      title: 'Smart Savings',
      description: 'Automatically calculates potential savings and highlights the best deals across all platforms.'
    }
  ];

  const techStack = [
    { category: 'Frontend', technologies: ['React', 'Tailwind CSS', 'Lucide Icons'] },
    { category: 'Backend', technologies: ['FastAPI', 'Python', 'Asyncio'] },
    { category: 'AI/ML', technologies: ['OpenAI API', 'Embeddings', 'Semantic Search'] },
    { category: 'Scraping', technologies: ['BeautifulSoup', 'aiohttp', 'Playwright'] },
    { category: 'Database', technologies: ['Pinecone', 'PostgreSQL', 'Redis'] }
  ];

  const platforms = [
    { name: 'Amazon India', description: 'Electronics, books, clothing & more' },
    { name: 'Flipkart', description: 'India\'s largest e-commerce marketplace' },
    { name: 'Blinkit', description: 'Quick commerce for groceries & essentials' },
    { name: 'Zepto', description: '10-minute grocery delivery' },
    { name: 'Instamart', description: 'Swiggy\'s instant grocery delivery' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            About CompareKart
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Built for the #BuildWithPuch Hackathon, CompareKart is an AI-powered price comparison 
            tool that helps consumers find the best deals across multiple e-commerce platforms.
          </p>
        </div>

        {/* Problem & Solution */}
        <div className="grid md:grid-cols-2 gap-12 mb-16">
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-red-100 p-2 rounded-lg">
                <Lightbulb className="h-6 w-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-semibold text-gray-900">The Problem</h2>
            </div>
            <p className="text-gray-600 mb-4">
              Consumers often have to manually check multiple e-commerce and quick commerce 
              platforms to find the lowest price for a product.
            </p>
            <ul className="text-gray-600 space-y-2">
              <li>• Product names vary between platforms</li>
              <li>• Time-consuming manual comparison</li>
              <li>• Missing out on better deals</li>
              <li>• No unified comparison tool</li>
            </ul>
          </div>

          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-green-100 p-2 rounded-lg">
                <Brain className="h-6 w-6 text-green-600" />
              </div>
              <h2 className="text-2xl font-semibold text-gray-900">Our Solution</h2>
            </div>
            <p className="text-gray-600 mb-4">
              CompareKart uses AI to automatically match products across platforms 
              and provides side-by-side price comparisons.
            </p>
            <ul className="text-gray-600 space-y-2">
              <li>• AI-powered semantic product matching</li>
              <li>• Real-time price comparison</li>
              <li>• Automatic savings calculation</li>
              <li>• Direct purchase links</li>
            </ul>
          </div>
        </div>

        {/* Features */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Key Features
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="card text-center">
                <div className="flex justify-center mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 text-sm">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Supported Platforms */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Supported Platforms
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {platforms.map((platform, index) => (
              <div key={index} className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {platform.name}
                </h3>
                <p className="text-gray-600 text-sm">
                  {platform.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Technology Stack
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {techStack.map((stack, index) => (
              <div key={index} className="card">
                <div className="flex items-center space-x-2 mb-4">
                  <Code className="h-5 w-5 text-primary-600" />
                  <h3 className="text-lg font-semibold text-gray-900">
                    {stack.category}
                  </h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {stack.technologies.map((tech, techIndex) => (
                    <span
                      key={techIndex}
                      className="px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm font-medium"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Team */}
        <div className="card text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Users className="h-6 w-6 text-primary-600" />
            <h2 className="text-3xl font-bold text-gray-900">Built for Hackathon</h2>
          </div>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            CompareKart was developed as part of the #BuildWithPuch Hackathon, 
            showcasing the power of AI in solving real-world e-commerce problems.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <span className="px-4 py-2 bg-gradient-to-r from-primary-50 to-success-50 text-primary-700 rounded-full font-medium">
              #BuildWithPuch
            </span>
            <span className="px-4 py-2 bg-gradient-to-r from-success-50 to-primary-50 text-success-700 rounded-full font-medium">
              AI-Powered
            </span>
            <span className="px-4 py-2 bg-gradient-to-r from-primary-50 to-warning-50 text-primary-700 rounded-full font-medium">
              Open Source
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
