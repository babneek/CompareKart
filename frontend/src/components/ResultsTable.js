import React from 'react';
import { ExternalLink, Star, TrendingDown, AlertCircle } from 'lucide-react';

const ResultsTable = ({ results }) => {
  if (!results) {
    return null;
  }

  const formatPrice = (price) => {
    if (!price) return 'N/A';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(price);
  };

  const getPlatformBadgeClass = (platform) => {
    const classes = {
      'Amazon': 'bg-orange-100 text-orange-800',
      'Myntra': 'bg-pink-100 text-pink-800',
      'Purplle': 'bg-purple-100 text-purple-800',
      'BigBasket': 'bg-green-100 text-green-800',
      'JioMart': 'bg-blue-100 text-blue-800',
      'Snapdeal': 'bg-red-100 text-red-800',
      'Zepto': 'bg-yellow-100 text-yellow-800',
      'Instamart': 'bg-indigo-100 text-indigo-800',
    };
    return `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${classes[platform] || 'bg-gray-100 text-gray-800'}`;
  };

  const renderPlatformProducts = (platforms) => {
    return Object.entries(platforms).map(([platform, products]) => (
      <div key={platform} className="mb-6">
        <h4 className="font-medium text-gray-900 mb-3 flex items-center">
          <span className={getPlatformBadgeClass(platform)}>
            {platform}
          </span>
          <span className="ml-2 text-sm text-gray-500">({products.length} products)</span>
        </h4>
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {products.slice(0, 6).map((product, idx) => (
            <div key={idx} className="bg-gray-50 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start space-x-3">
                {product.image && (
                  <img 
                    src={product.image} 
                    alt={product.title}
                    className="w-16 h-16 object-cover rounded-md flex-shrink-0"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                )}
                <div className="flex-1 min-w-0">
                  <h5 className="text-sm font-medium text-gray-900 line-clamp-2 mb-2">
                    {product.title}
                  </h5>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold text-gray-900">
                      {formatPrice(product.price)}
                    </span>
                    
                    {product.url && (
                      <a
                        href={product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    )}
                  </div>
                  
                  {product.rating && (
                    <div className="flex items-center mt-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      <span className="text-sm text-gray-600 ml-1">{product.rating}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    ));
  };

  const renderComparisons = () => {
    if (!results.comparisons || results.comparisons.length === 0) {
      return (
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Found</h3>
          <p className="text-gray-600">
            Try searching for a different product or adjusting your filters.
          </p>
        </div>
      );
    }

    return results.comparisons.map((comparison, index) => (
      <div key={index} className="bg-white rounded-xl shadow-lg p-6 mb-6">
        {comparison.platforms && typeof comparison.platforms === 'object' ? (
          // Individual products grouped by platform
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              {comparison.product_name}
            </h3>
            {comparison.note && (
              <p className="text-gray-600 mb-6 italic">{comparison.note}</p>
            )}
            {renderPlatformProducts(comparison.platforms)}
          </div>
        ) : (
          // Matched products across platforms
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">
                {comparison.product_name}
              </h3>
              {comparison.savings_amount > 0 && (
                <div className="flex items-center text-green-600">
                  <TrendingDown className="h-5 w-5 mr-1" />
                  <span className="font-medium">
                    Save {formatPrice(comparison.savings_amount)} ({comparison.savings_percentage}%)
                  </span>
                </div>
              )}
            </div>

            {comparison.price_stats && (
              <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">
                    {formatPrice(comparison.price_stats.min_price)}
                  </p>
                  <p className="text-sm text-gray-600">Best Price</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">
                    {formatPrice(comparison.price_stats.avg_price)}
                  </p>
                  <p className="text-sm text-gray-600">Average Price</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">
                    {formatPrice(comparison.price_stats.max_price)}
                  </p>
                  <p className="text-sm text-gray-600">Highest Price</p>
                </div>
              </div>
            )}

            {comparison.best_deal && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-green-900">Best Deal</h4>
                    <p className="text-sm text-green-700">{comparison.best_deal.title}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-green-600">
                      {formatPrice(comparison.best_deal.price)}
                    </p>
                    <span className={getPlatformBadgeClass(comparison.best_deal.platform)}>
                      {comparison.best_deal.platform}
                    </span>
                  </div>
                  {comparison.best_deal.url && (
                    <a
                      href={comparison.best_deal.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-4 inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Buy Now
                      <ExternalLink className="h-4 w-4 ml-2" />
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    ));
  };

  return (
    <div className="space-y-6">
      {renderComparisons()}
    </div>
  );
};

export default ResultsTable;
