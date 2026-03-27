/**
 * MarketPharm Product Interactions
 * Handles Likes, Recommendations and Ratings via AJAX
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('MarketPharm Interactions JS Loaded 1.1');

    // Generic toggle function
    const toggleInteraction = async (productId, endpoint, btnElement, countElement, activeClass, countKey) => {
        console.log(`Toggling ${endpoint} for product ${productId}`);
        // alert(`Tentative: ${endpoint} pour produit ${productId}`); // Heavy debug

        try {
            const response = await fetch(`/api/products/${productId}/${endpoint}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                    // CSRF is exempt on backend now, but headers are fine
                }
            });

            if (response.status === 401 || response.status === 403) {
                alert('Session expirée ou non autorisée. Veuillez vous reconnecter.');
                window.location.href = '/login/?next=' + window.location.pathname;
                return;
            }

            const data = await response.json();
            console.log('Response data:', data);
            
            if (response.ok) {
                // Update UI based on what the API returns
                // The API for likes returns {liked: true/false, likes_count: n}
                // The API for recommends returns {recommended: true/false, user_recommendations: n}
                
                if (data.liked !== undefined) {
                    btnElement.classList.toggle(activeClass, data.liked);
                    console.log(`Liked class toggled to: ${data.liked}`);
                }
                
                if (data.recommended !== undefined) {
                    btnElement.classList.toggle(activeClass, data.recommended);
                    // Update icon too
                    const icon = btnElement.querySelector('i');
                    if (icon) {
                        if (data.recommended) {
                            icon.classList.remove('fa-regular');
                            icon.classList.add('fas');
                        } else {
                            icon.classList.remove('fas');
                            icon.classList.add('fa-regular');
                        }
                    }
                }
                
                if (countElement) {
                    // Try different keys from API
                    const newCount = data[countKey] !== undefined ? data[countKey] : 
                                   (data.likes_count !== undefined ? data.likes_count : 
                                    (data.user_recommendations !== undefined ? data.user_recommendations : null));
                    
                    if (newCount !== null) {
                        countElement.textContent = newCount;
                    }
                }
                
                // alert('Succès: ' + (data.message || 'Action effectuée'));
            } else {
                alert('Erreur du serveur: ' + (data.error || 'Inconnue'));
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('Erreur de connection: ' + error.message);
        }
    };

    // Use event delegation on body or main container
    document.addEventListener('click', (e) => {
        // Like Button
        const likeBtn = e.target.closest('.btn-like-toggle');
        if (likeBtn) {
            e.preventDefault();
            const productId = likeBtn.dataset.productId;
            toggleInteraction(productId, 'like', likeBtn, null, 'active', 'likes_count');
            return;
        }

        // Recommend Button
        const recommendBtn = e.target.closest('.btn-recommend-toggle');
        if (recommendBtn) {
            e.preventDefault();
            const productId = recommendBtn.dataset.productId;
            const countSpan = recommendBtn.querySelector('.recommendation-count');
            toggleInteraction(productId, 'recommend', recommendBtn, countSpan, 'active', 'user_recommendations');
            return;
        }

        // Star Rating handled separately or similarly
        const star = e.target.closest('.star-rating i');
        if (star) {
            const container = star.closest('.star-rating');
            const productId = container.dataset.productId;
            const rating = star.dataset.rating;
            // ... direct call for rating because it reloads anyway
            handleRating(productId, rating);
        }
        
        // Delete Rating
        const deleteBtn = e.target.closest('.btn-delete-rating');
        if (deleteBtn) {
            e.preventDefault();
            const productId = deleteBtn.dataset.productId;
            handleUnrate(productId);
        }
    });

    async function handleRating(productId, rating) {
        try {
            const response = await fetch(`/api/products/${productId}/rate/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rating: parseInt(rating) })
            });
            if (response.ok) { location.reload(); }
            else { alert('Erreur rating'); }
        } catch (e) { alert('Exception rating'); }
    }

    async function handleUnrate(productId) {
        if (!confirm('Supprimer ?')) return;
        try {
            const response = await fetch(`/api/products/${productId}/unrate/`, { method: 'POST' });
            if (response.ok) { location.reload(); }
        } catch (e) { alert('Exception unrate'); }
    }
});
