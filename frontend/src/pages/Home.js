import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import SearchForm from '../components/SearchForm';
import ResultsTable from '../components/ResultsTable';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const Home = () => {
  const [searchResults, setSearchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = async (searchParams) => {
    setIsLoading(true);
    setSearchQuery(searchParams.product);
    
    try {
      console.log('Starting search with params:', searchParams);
      
      const results = await apiService.compareProducts(
        searchParams.product,
        searchParams.category,
        searchParams.platforms,
        searchParams.maxResults
      );
      
      console.log('Search results:', results);
      setSearchResults(results);
      
      if (results.comparisons && results.comparisons.length > 0) {
        toast.success(`Found ${results.total_comparisons} product comparisons!`);
      } else {
        toast.info('No products found. Try different keywords or platforms.');
      }
      
    } catch (error) {
      console.error('Search error:', error);
      
      let errorMessage = 'Failed to search products. Please try again.';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
      setSearchResults(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#4ade80',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
            Compare<span className="text-blue-600">Kart</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            🎯 Compare prices. Shop smart. Save more.
          </p>
          <p className="text-gray-500 mt-2">
            AI-powered price comparison across India's top e-commerce platforms
          </p>
        </div>

        {/* Search Form */}
        <SearchForm onSearch={handleSearch} isLoading={isLoading} />

        {/* Search Results */}
        {searchResults && (
          <div className="mt-8">
            {/* Search Summary */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-800">
                    Search Results for "{searchQuery}"
                  </h3>
                  <p className="text-gray-600">
                    {searchResults.category && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800 mr-2">
                        Category: {searchResults.category}
                      </span>
                    )}
                    Found {searchResults.total_comparisons} comparisons across {searchResults.platforms_searched?.length || 0} platforms
                  </p>
                </div>
                
                {searchResults.best_overall_deal && (
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Best Deal</p>
                    <p className="text-2xl font-bold text-green-600">
                      ₹{searchResults.best_overall_deal.price?.toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-500">
                      on {searchResults.best_overall_deal.platform}
                    </p>
                  </div>
                )}
              </div>
              
              {searchResults.total_savings > 0 && (
                <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
                  <p className="text-green-800 font-medium">
                    💰 Total Potential Savings: ₹{searchResults.total_savings.toLocaleString()}
                  </p>
                </div>
              )}
            </div>

            {/* Platform Results Summary */}
            {searchResults.platform_results && (
              <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                <h4 className="text-lg font-semibold text-gray-800 mb-4">Platform Coverage</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  {Object.entries(searchResults.platform_results).map(([platform, count]) => {
                    const platformName = platform.replace('_count', '').replace(/^\w/, c => c.toUpperCase());
                    return (
                      <div key={platform} className="text-center p-3 bg-gray-50 rounded-lg">
                        <p className="font-medium text-gray-800">{platformName}</p>
                        <p className="text-2xl font-bold text-blue-600">{count}</p>
                        <p className="text-xs text-gray-500">products</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Results Table */}
            <ResultsTable results={searchResults} />
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600 font-medium">Searching across platforms...</p>
              <p className="text-sm text-gray-500 mt-1">This may take a few seconds</p>
            </div>
          </div>
        )}

        {/* No Results State */}
        {searchResults && (!searchResults.comparisons || searchResults.comparisons.length === 0) && !isLoading && (
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">No Products Found</h3>
            <p className="text-gray-600 mb-4">
              We couldn't find any products matching your search criteria.
            </p>
            <div className="text-sm text-gray-500">
              <p>Try:</p>
              <ul className="mt-2 space-y-1">
                <li>• Using different keywords</li>
                <li>• Selecting more platforms</li>
                <li>• Choosing a different category</li>
                <li>• Checking spelling</li>
              </ul>
            </div>
          </div>
        )}

        {/* Features Section */}
        {!searchResults && !isLoading && (
          <div className="mt-12 grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Smart Categories</h3>
              <p className="text-gray-600">
                Choose from specialized categories like Fashion, Beauty, Groceries, and more for targeted results.
              </p>
            </div>
            
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Lightning Fast</h3>
              <p className="text-gray-600">
                Get real-time price comparisons across multiple platforms in seconds with our optimized search.
              </p>
            </div>
            
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-4xl mb-4">💰</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Best Deals</h3>
              <p className="text-gray-600">
                Automatically highlights the best deals and shows you exactly how much you can save.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
