document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('cheatTableBody');
    const loadingSpinner = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const sortBtn = document.getElementById('sortBtn');
    let pairsData = [];
    let sortAscending = false;

    // Function to get percentage class for styling
    const getPercentageClass = (percentage) => {
        if (percentage >= 80) return 'percentage-high';
        if (percentage >= 50) return 'percentage-medium';
        if (percentage > 0) return 'percentage-low';
        return 'percentage-no-cheat';
    };

    // Function to get time class for styling
    const getTimeClass = (Time) => {
        if (Time <= 10) return 'percentage-high';
        if (Time <= 30) return 'percentage-medium';
        if (Time <= 60) return 'percentage-low';
        return 'percentage-no-cheat';
    };

    // Function to render table
    const renderTable = (pairs) => {
        tableBody.innerHTML = '';
        pairs.forEach((pair, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <button class="btn btn-link toggle-details" data-index="${index}" aria-expanded="false" aria-label="Toggle details for ${pair.student1} and ${pair.student2}">
                        ${pair.student1} & ${pair.student2}
                    </button>
                </td>
                <td class="text-end ${getPercentageClass(pair.overall_percentage)}">
                    ${pair.overall_percentage}%
                </td>
            `;
            tableBody.appendChild(row);

            // Add details row
            const detailsRow = document.createElement('tr');
            detailsRow.className = 'question-details';
            detailsRow.id = `details-${index}`;
            detailsRow.innerHTML = `
                <td colspan="2">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Question</th>
                                <th>Answer 1</th>
                                <th>Answer 2</th>
                                <th>SBERT Similarity</th>
                                <th>TF-IDF Similarity</th>
                                <th>Diff Similarity</th>
                                <th>Time Diff (s)</th>
                                <th>Cheating Likelihood (%)</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${pair.answers_comparison.map(q => `
                                <tr>
                                    <td>${q.qnumber}</td>
                                    <td>${q.answer1}</td>
                                    <td>${q.answer2}</td>
                                    <td class="${getPercentageClass(q.cosine_similarity_sbert * 100)}">
                                        ${(q.cosine_similarity_sbert * 100).toFixed(2)}%
                                    </td>
                                    <td class="${getPercentageClass(q.cosine_similarity_tfidf * 100)}">
                                        ${(q.cosine_similarity_tfidf * 100).toFixed(2)}%
                                    </td>
                                    <td class="${getPercentageClass(q.diff_similarity * 100)}">
                                        ${(q.diff_similarity * 100).toFixed(2)}%
                                    </td>
                                    <td class=${getTimeClass(q.time_difference)}>${q.time_difference !== null ? q.time_difference : 'N/A'}</td>
                                    <td class="${getPercentageClass(q.question_cheating_percentage)}">
                                        ${q.question_cheating_percentage}%
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </td>
            `;
            tableBody.appendChild(detailsRow);
        });
    };

    // Function to sort pairs
    const sortPairs = () => {
        pairsData.sort((a, b) => {
            if (sortAscending) {
                return a.overall_percentage - b.overall_percentage;
            }
            return b.overall_percentage - a.overall_percentage;
        });
        sortBtn.querySelector('svg').classList.toggle('bi-sort-down', !sortAscending);
        sortBtn.querySelector('svg').classList.toggle('bi-sort-up', sortAscending);
        renderTable(pairsData);
    };

    // Toggle sort direction
    sortBtn.addEventListener('click', () => {
        sortAscending = !sortAscending;
        sortPairs();
    });

    // Event delegation for toggle buttons
    tableBody.addEventListener('click', (e) => {
        const btn = e.target.closest('.toggle-details');
        if (btn) {
            const index = btn.dataset.index;
            const detailsRow = document.getElementById(`details-${index}`);
            const isExpanded = btn.getAttribute('aria-expanded') === 'true';
            detailsRow.classList.toggle('show', !isExpanded);
            btn.setAttribute('aria-expanded', !isExpanded);
        }
    });

    // Fetch data from API
    const fetchData = async () => {
        loadingSpinner.style.display = 'block';
        errorDiv.style.display = 'none';
        try {
            const response = await fetch('http://localhost:5000/cheat_detection');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            pairsData = data.pairs || [];
            renderTable(pairsData);
        } catch (err) {
            errorDiv.textContent = `Error: ${err.message}`;
            errorDiv.style.display = 'block';
            tableBody.innerHTML = '';
        } finally {
            loadingSpinner.style.display = 'none';
        }
    };

    // Initial fetch
    fetchData();
});