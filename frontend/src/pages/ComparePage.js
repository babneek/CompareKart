import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, ExternalLink, TrendingDown, Clock, Star, AlertCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiService } from '../services/api';

const ComparePage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const query = searchParams.get('q');
    if (query && query !== searchQuery) {
      setSearchQuery(query);
      handleSearch(query);
    }
  }, [searchParams]);

  const handleSearch = async (query = searchQuery) => {
    if (!query.trim()) {
      toast.error('Please enter a product name to search');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await apiService.compareProducts(query.trim(), null, null, 5);
      setResults(data);
      
      if (data.comparisons && data.comparisons.length > 0) {
        toast.success(`Found ${data.comparisons.length} product comparison(s)`);
      } else {
        toast.info('No matching products found across platforms');
      }
      
      // Update URL
      setSearchParams({ q: query.trim() });
    } catch (err) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSearch();
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(price);
  };

  const getPlatformBadgeClass = (platform) => {
    const classes = {
      'Amazon': 'platform-amazon',
      'Flipkart': 'platform-flipkart',
      'Blinkit': 'platform-blinkit',
    };
    return `platform-badge ${classes[platform] || 'bg-gray-100 text-gray-800'}`;
  };

  const renderPlatformProducts = (platforms) => {
    return Object.entries(platforms).map(([platform, products]) => (
      <div key={platform} className="space-y-3">
        <h4 className="font-medium text-gray-900 flex items-center space-x-2">
          <span className={getPlatformBadgeClass(platform)}>
            {platform}
          </span>
          <span className="text-sm text-gray-500">({products.length} products)</span>
        </h4>
        
        <div className="space-y-2">
          {products.slice(0, 3).map((product, idx) => (
            <div key={idx} className="bg-gray-50 rounded-lg p-3 flex justify-between items-center">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {product.title}
                </p>
                <div className="flex items-center space-x-4 mt-1">
                  <span className="text-lg font-bold text-gray-900">
                    {formatPrice(product.price)}
                  </span>
                  {product.rating && (
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      <span className="text-sm text-gray-600">{product.rating}</span>
                    </div>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-1">{product.delivery_info}</p>
              </div>
              
              {product.url && (
                <a
                  href={product.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary text-sm py-1 px-3 flex items-center space-x-1"
                >
                  <span>Buy</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    ));
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Search Header */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Compare Products</h1>
          
          <form onSubmit={handleSubmit} className="max-w-2xl">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for any product... (e.g., iPhone 15, Maggi noodles)"
                className="input-field pr-16"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading}
                className="absolute right-2 top-2 bottom-2 btn-primary px-4 flex items-center space-x-2 disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
                <span className="hidden sm:inline">
                  {loading ? 'Searching...' : 'Search'}
                </span>
              </button>
            </div>
          </form>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary-600 mx-auto mb-4" />
            <p className="text-gray-600">Searching across platforms...</p>
            <p className="text-sm text-gray-500 mt-2">This may take a few seconds</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
            <div className="flex items-center space-x-2 text-red-800">
              <AlertCircle className="h-5 w-5" />
              <h3 className="font-medium">Search Error</h3>
            </div>
            <p className="text-red-700 mt-2">{error}</p>
          </div>
        )}

        {/* Results */}
        {results && !loading && (
          <div className="space-y-8">
            {/* Search Summary */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  Search Results for "{results.query}"
                </h2>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <Clock className="h-4 w-4" />
                  <span>{new Date(results.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary-600">{results.total_comparisons}</p>
                  <p className="text-sm text-gray-600">Comparisons Found</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-success-600">
                    {formatPrice(results.total_savings || 0)}
                  </p>
                  <p className="text-sm text-gray-600">Total Savings</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">
                    {results.platform_results?.amazon_count + results.platform_results?.flipkart_count + results.platform_results?.blinkit_count || 0}
                  </p>
                  <p className="text-sm text-gray-600">Products Found</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{results.platforms_searched?.length || 0}</p>
                  <p className="text-sm text-gray-600">Platforms Searched</p>
                </div>
              </div>
            </div>

            {/* Best Deal Highlight */}
            {results.best_overall_deal && (
              <div className="bg-gradient-to-r from-success-50 to-primary-50 border border-success-200 rounded-xl p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <TrendingDown className="h-6 w-6 text-success-600" />
                  <h3 className="text-xl font-semibold text-gray-900">Best Deal Found!</h3>
                </div>
                
                <div className="bg-white rounded-lg p-4 flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-2">
                      {results.best_overall_deal.title}
                    </h4>
                    <div className="flex items-center space-x-4">
                      <span className="text-3xl font-bold text-success-600">
                        {formatPrice(results.best_overall_deal.price)}
                      </span>
                      <span className={getPlatformBadgeClass(results.best_overall_deal.platform)}>
                        {results.best_overall_deal.platform}
                      </span>
                      {results.best_overall_deal.rating && (
                        <div className="flex items-center space-x-1">
                          <Star className="h-4 w-4 text-yellow-400 fill-current" />
                          <span className="text-sm text-gray-600">{results.best_overall_deal.rating}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {results.best_overall_deal.url && (
                    <a
                      href={results.best_overall_deal.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-primary flex items-center space-x-2"
                    >
                      <span>Buy Now</span>
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  )}
                </div>
              </div>
            )}

            {/* Detailed Comparisons */}
            {results.comparisons && results.comparisons.length > 0 ? (
              <div className="space-y-6">
                <h3 className="text-2xl font-semibold text-gray-900">Detailed Comparisons</h3>
                
                {results.comparisons.map((comparison, index) => (
                  <div key={index} className="card">
                    <div className="flex items-center justify-between mb-6">
                      <h4 className="text-xl font-semibold text-gray-900">
                        {comparison.product_name}
                      </h4>
                      {comparison.savings_amount > 0 && (
                        <div className="savings-badge">
                          Save {formatPrice(comparison.savings_amount)} ({comparison.savings_percentage?.toFixed(1)}%)
                        </div>
                      )}
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {renderPlatformProducts(comparison.platforms)}
                    </div>

                    {comparison.price_stats && (
                      <div className="mt-6 pt-6 border-t border-gray-200">
                        <div className="grid grid-cols-3 gap-4 text-center">
                          <div>
                            <p className="text-lg font-semibold text-gray-900">
                              {formatPrice(comparison.price_stats.min_price)}
                            </p>
                            <p className="text-sm text-gray-600">Lowest Price</p>
                          </div>
                          <div>
                            <p className="text-lg font-semibold text-gray-900">
                              {formatPrice(comparison.price_stats.avg_price)}
                            </p>
                            <p className="text-sm text-gray-600">Average Price</p>
                          </div>
                          <div>
                            <p className="text-lg font-semibold text-gray-900">
                              {formatPrice(comparison.price_stats.max_price)}
                            </p>
                            <p className="text-sm text-gray-600">Highest Price</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : results.comparisons && results.comparisons[0]?.individual_products ? (
              <div className="card">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  Individual Results
                </h3>
                <p className="text-gray-600 mb-6">
                  {results.comparisons[0].note}
                </p>
                
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {renderPlatformProducts(results.comparisons[0].platforms)}
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Found</h3>
                <p className="text-gray-600">
                  Try searching for a different product or check your spelling.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ComparePage;
