# Masmorra do D20

RPG de turno no navegador, inspirado em RPG de mesa com d20. É um único `index.html`, sem instalação e sem servidor. Feito para jogar em sala: projetado na lousa, com cada herói controlado por uma pessoa ou por um grupo da turma.

## Como abrir

- **Offline:** baixe `index.html` e abra no navegador. Funciona sem internet; só as fontes caem para as do sistema.
- **Online pelo GitHub Pages:** em *Settings → Pages*, escolha *Deploy from a branch*, o branch deste trabalho e a pasta raiz. O jogo fica em `https://<usuário>.github.io/<repositório>/masmorra-d20/`.

## O jogo

- Grupo de 1 a 4 heróis: Guerreiro, Mago, Ladino e Clérigo. Dá para rolar atributos (4d6, descarta o menor) ou usar os valores padrão.
- Cinco cenas até o chefe, Malvek, o Necromante. Depois de cada vitória o grupo sobe de nível e descansa.
- Regras simplificadas: iniciativa, jogada de ataque contra CA, crítico com 20 natural, vantagem e desvantagem, teste de resistência contra CD, espaços de magia, ação e ação bônus, testes contra a morte.
- Cada rolagem aparece na bandeja de dados e no diário com a conta inteira (`d20 14 + 5 = 19 contra CA 15`), para dar para discutir a matemática com a turma.
- Três dificuldades. Grupos de 1 ou 2 heróis ganham PV extras para compensar.
- O progresso fica salvo no navegador. Recarregar a página não perde a aventura.

## Acessibilidade

- Tudo funciona por teclado. Na vez de cada herói, o foco vai para o painel de ações. `Esc` cancela a escolha de alvo.
- O diário de combate é uma região `role="log"`, lida por leitores de tela a cada jogada.
- Contraste de texto acima de 5,6:1 nos temas claro e escuro. Alvos de toque com pelo menos 48 px.
- Opção "Texto grande" para projetor. `prefers-reduced-motion` desliga as animações.
- Estado nunca depende só de cor: caído, esquivando, abençoado e derrotado aparecem escritos.

## Balanceamento

Testado com um jogador automático em 40 campanhas por tamanho de grupo e dificuldade. Taxa de vitória do robô: Fácil perto de 100%, Normal perto de 95% (com heróis caindo de 3 a 5 vezes por campanha nos grupos de 3 e 4), Difícil entre 50% e 90% conforme o grupo. Uma turma joga pior que o robô, então o Normal tende a ser mais apertado na prática.

## Créditos

Este trabalho inclui material adaptado do System Reference Document 5.1 ("SRD 5.1") da Wizards of the Coast LLC, disponível em https://dnd.wizards.com/resources/systems-reference-document. O SRD 5.1 é licenciado sob a Creative Commons Attribution 4.0 International License, disponível em https://creativecommons.org/licenses/by/4.0/legalcode. O jogo não tem vínculo com a Wizards of the Coast.

Fontes: Grenze Gotisch, Grenze, Atkinson Hyperlegible Next e Atkinson Hyperlegible Mono, via Google Fonts (SIL Open Font License).
