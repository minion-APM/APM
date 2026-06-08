document.addEventListener("DOMContentLoaded", function () {
    const dados = window.dashboardData || {
        produtos: 0,
        categorias: 0,
        usuarios: 0,
        movimentacoes: 0
    };

    const ctx = document.getElementById("vendasChart");

    if (ctx) {
        new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: ["Produtos", "Categorias", "Usuários", "Movimentações"],
                datasets: [{
                    data: [
                        dados.produtos,
                        dados.categorias,
                        dados.usuarios,
                        dados.movimentacoes
                    ],
                    backgroundColor: [
                        "#2563eb", // Azul - Produtos
                        "#ff7a00", // Laranja - Categorias
                        "#111827", // Escuro - Usuários
                        "#9ca3af"  // Cinza - Movimentações
                    ],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "right",
                        labels: {
                            boxWidth: 12,
                            padding: 15,
                            font: {
                                size: 13,
                                family: "sans-serif"
                            }
                        }
                    }
                }
            }
        });
    }
});