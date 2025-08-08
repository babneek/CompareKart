import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, TrendingUp, Shield, Zap, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';

const HomePage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      toast.error('Please enter a product name to search');
      return;
    }
    
    navigate(`/compare?q=${encodeURIComponent(searchQuery.trim())}`);
  };

  const popularSearches = [
    'iPhone 15',
    'Samsung Galaxy S24',
    'Maggi Noodles',
    'Surf Excel',
    'Amul Milk',
    'Britannia Bread'
  ];

  const features = [
    {
      icon: <Search className="h-8 w-8 text-primary-600" />,
      title: 'Smart AI Search',
      description: 'Our AI understands your search and finds the best matching products across platforms'
    },
    {
      icon: <TrendingUp className="h-8 w-8 text-success-600" />,
      title: 'Best Price Guarantee',
      description: 'Compare prices from Amazon, Flipkart, Blinkit, and more to find the lowest price'
    },
    {
      icon: <Zap className="h-8 w-8 text-warning-600" />,
      title: 'Lightning Fast',
      description: 'Get price comparisons in seconds with our optimized scraping technology'
    },
    {
      icon: <Shield className="h-8 w-8 text-blue-600" />,
      title: 'Always Updated',
      description: 'Real-time price tracking ensures you always get the most current deals'
    }
  ];

  const platforms = [
    { name: 'Amazon', logo: '🛒', color: 'bg-orange-100 text-orange-800' },
    { name: 'Flipkart', logo: '🛍️', color: 'bg-blue-100 text-blue-800' },
    { name: 'Blinkit', logo: '⚡', color: 'bg-yellow-100 text-yellow-800' },
    { name: 'Zepto', logo: '🚀', color: 'bg-purple-100 text-purple-800' },
    { name: 'Instamart', logo: '📦', color: 'bg-green-100 text-green-800' }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 via-white to-success-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Compare prices.
              <br />
              <span className="text-primary-600">Shop smart.</span>
              <br />
              <span className="text-success-600">Save more.</span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
              Find the best deals across all major e-commerce platforms with our AI-powered 
              price comparison tool. Never overpay again!
            </p>

            {/* Search Form */}
            <form onSubmit={handleSearch} className="max-w-2xl mx-auto mb-8">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search for any product... (e.g., iPhone 15, Maggi noodles)"
                  className="input-field pr-16 text-lg py-4"
                />
                <button
                  type="submit"
                  className="absolute right-2 top-2 bottom-2 btn-primary px-6 flex items-center space-x-2"
                >
                  <Search className="h-5 w-5" />
                  <span className="hidden sm:inline">Search</span>
                </button>
              </div>
            </form>

            {/* Popular Searches */}
            <div className="mb-12">
              <p className="text-gray-600 mb-4">Popular searches:</p>
              <div className="flex flex-wrap justify-center gap-2">
                {popularSearches.map((search) => (
                  <button
                    key={search}
                    onClick={() => {
                      setSearchQuery(search);
                      navigate(`/compare?q=${encodeURIComponent(search)}`);
                    }}
                    className="px-4 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-700 hover:border-primary-300 hover:text-primary-600 transition-colors duration-200"
                  >
                    {search}
                  </button>
                ))}
              </div>
            </div>

            {/* Platforms */}
            <div className="mb-16">
              <p className="text-gray-600 mb-6">Compare prices across:</p>
              <div className="flex flex-wrap justify-center gap-4">
                {platforms.map((platform) => (
                  <div
                    key={platform.name}
                    className={`px-4 py-2 rounded-full ${platform.color} flex items-center space-x-2`}
                  >
                    <span className="text-lg">{platform.logo}</span>
                    <span className="font-medium">{platform.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Why Choose CompareKart?
            </h2>
            <p className="text-xl text-gray-600">
              Powered by AI, built for savings
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="card text-center hover:shadow-md transition-shadow duration-200">
                <div className="flex justify-center mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to start saving money?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Join thousands of smart shoppers who use CompareKart to find the best deals
          </p>
          <button
            onClick={() => navigate('/compare')}
            className="bg-white text-primary-600 hover:bg-gray-100 font-semibold py-4 px-8 rounded-lg text-lg flex items-center space-x-2 mx-auto transition-colors duration-200"
          >
            <span>Start Comparing Now</span>
            <ArrowRight className="h-5 w-5" />
          </button>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
