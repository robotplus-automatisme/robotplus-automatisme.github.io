---
layout: page
title: "Solutions"
description: "Robotique industrielle, contrôle, marquage laser, alimentation de pièces, postes de travail et machines spéciales."
---
<div class="page-intro"><div class="eyebrow">Savoir-faire</div><h1>Des solutions pensées pour la production.</h1><p class="lead">Les principales familles de solutions présentées dans la documentation ROBOT+.</p></div>
<section class="section"><div class="container"><div class="cards cards-2">{% assign solutions = site.solutions | sort: "order" %}{% for solution in solutions %}<article class="solution-card"><span class="solution-index">{{ solution.order | prepend: "0" | slice: -2, 2 }}</span><h2>{{ solution.title }}</h2><p>{{ solution.excerpt }}</p><a class="text-link" href="{{ solution.url | relative_url }}">Voir la solution →</a></article>{% endfor %}</div></div></section>
