Aquí tienes el análisis detallado del paper científico, estructurado y formateado en Markdown con fórmulas en LaTeX, listo para ser utilizado como base teórica para la programación del modelo en Python.

### 1. Título del paper y Autores
*   **Título:** Multi-Market, Multi-Product New Product Diffusion: Decomposing Local, Foreign, and Indirect (Cross-Product) Effects.
*   **Autores:** Antonio Ladrón-de-Guevara & William P. Putsis.

---

### 2. Definición Matemática del Modelo de Difusión Propuesto

El modelo propuesto extiende el modelo clásico de Bass al hacer que el **mercado potencial sea endógeno y dinámico**. La adopción de un producto $x$ en un país $i$ no solo depende de los usuarios locales, sino también de los usuarios extranjeros (efectos de red cruzados entre países) y de los usuarios de un producto complementario $y$ (efectos de red indirectos o cruzados entre productos).

#### A. Mercado Potencial Dinámico
El mercado potencial en el instante $t$, denotado como $M_{xi}(t)$, se define como la proporción del sistema social que es susceptible de adoptar la innovación:

$$ M_{xi}(t) = C_{xi}(t) S_{xi}(t) $$

Donde la fracción acumulada del sistema social dispuesta a adoptar, $C_{xi}(t)$, crece exponencialmente en función de tres "piscinas" de adopción previa (efectos de red):

$$ C_{xi}(t) = 1 - \theta_x \exp\left[ - \left( \gamma_x \left( \frac{N_{xi}(t)}{S_{xi}(t)} \right) + \widetilde{\gamma}_x \left( \frac{\sum_{j \neq i} N_{xj}(t)}{\sum_{j \neq i} S_{xj}(t)} \right) + \widehat{\gamma}_{xy} \left( \frac{N_{yi}(t)}{S_{yi}(t)} \right) \right) \right] $$

#### B. Ecuación de Difusión (Nuevos Adoptantes)
El número de nuevos adoptantes en el período $t$, basado en una estructura discreta del modelo de Bass generalizado, se define como:

$$ n_{xi}(t) = \left[ \alpha_{xi} + \beta_{xi} \frac{N_{xi}(t-1)}{M_{xi}(t-1)} \right] \left[ M_{xi}(t-1) - N_{xi}(t-1) \right] $$

#### C. Inclusión de Covariables (Variables de control)
El paper especifica (en la nota al pie 5 y sección 2.3) que las covariables exógenas (como Precio, PIB/PIB per cápita y Factores Culturales) entran linealmente a través del **coeficiente de influencia interna** $\beta_{xi}$. Para programarlo, esto se modela como:

$$ \beta_{xi}(t) = \beta_{0,xi} + \delta_1 \text{PIB}_{i}(t) + \delta_2 \text{Precio}_{i}(t) + \delta_3 \text{Cultura}_{i} $$

#### D. Efectos Indirectos Dinámicos (Variantes en el tiempo)
El modelo permite que el efecto cruzado entre productos varíe a lo largo del tiempo (por ejemplo, el efecto del PC sobre el Internet cambia a medida que ambas tecnologías maduran). Esto se formula mediante una función exponencial decreciente/creciente:

$$ \widehat{\gamma}(t) = \widehat{\gamma}_0 \cdot 0.5^{\left( \phi |\phi|^{(t-T_0)} \right)} $$
*(Nota: En el paper, $T_0 = 1992$ corresponde al año base para el inicio del Internet).*

---

### 3. Explicación Detallada de cada Parámetro del Modelo

Para implementar este modelo en Python, necesitarás definir y optimizar los siguientes parámetros y variables de estado:

#### Variables de Estado (Datos de entrada)
*   $t$: Período de tiempo (año).
*   $n_{xi}(t)$: Número de **nuevos adoptantes** del producto $x$ en el país $i$ durante el período $t$.
*   $N_{xi}(t)$: Número **acumulado de adoptantes** del producto $x$ en el país $i$ al inicio del período $t$.
*   $S_{xi}(t)$: Tamaño del **sistema social** (población total o número de hogares) para el producto $x$ en el país $i$ en el tiempo $t$.
*   $\sum_{j \neq i} N_{xj}(t)$: Número acumulado de usuarios del producto $x$ en el **extranjero** (todos los países $j$ excepto $i$).
*   $\sum_{j \neq i} S_{xj}(t)$: Tamaño total del sistema social extranjero.
*   $N_{yi}(t)$: Número acumulado de adoptantes del **producto complementario** $y$ (ej. Internet) en el país $i$.
*   $S_{yi}(t)$: Tamaño del sistema social para el producto complementario $y$.

#### Parámetros Estructurales a Estimar
*   $M_{xi}(t)$: **Mercado potencial** dinámico. Representa el límite superior temporal de adoptantes.
*   $C_{xi}(t)$: Fracción del mercado "susceptible" a la adopción ($0 \leq C_{xi}(t) \leq 1$). Actúa como un parámetro de "techo".
*   $\alpha_{xi}$: **Coeficiente de influencia externa** (similar al parámetro $p$ en Bass). Mide la adopción por innovación pura, independiente de las interacciones sociales.
*   $\beta_{xi}$: **Coeficiente de influencia interna** (similar al parámetro $q$ en Bass). Mide la adopción impulsada por el boca a boca y la imitación social local.
*   $\theta_x$: **Parámetro de adoptantes tempranos**. Determina el tamaño inicial del mercado potencial cuando las redes son de tamaño cero. Matemáticamente, el techo inicial es $(1 - \theta_x)$.

#### Parámetros de Efectos de Red (El núcleo de la contribución del paper)
*   $\gamma_x$: **Efecto de red directo local**. Mide el impacto del tamaño de la base instalada del mismo producto dentro del mismo país sobre el crecimiento del mercado potencial.
*   $\widetilde{\gamma}_x$: **Efecto de red directo extranjero (Cross-country)**. Mide el impacto de la base de usuarios en otros países sobre el mercado local.
*   $\widehat{\gamma}_{xy}$: **Efecto de red indirecto (Cross-product)**. Mide la complementariedad; cómo la base instalada del producto $y$ afecta la disposición a adoptar el producto $x$. (Se espera que sea $>0$ para bienes complementarios, cerca de $0$ para independientes, y $<0$ para sustitutos).

#### Parámetros de Dinámica Temporal
*   $\widehat{\gamma}_0$: Valor asintótico a largo plazo del efecto cruzado entre productos.
*   $\phi$: Parámetro de forma que determina qué tan rápido y en qué dirección evoluciona el efecto indirecto a lo largo del tiempo (si $\phi > 0$, el efecto crece; si $\phi < 0$, se disipa; si $\phi = 0$, es constante).

---

### 4. ¿Cómo se diferencia de los Modelos Clásicos?

Este framework fue diseñado intencionalmente para anidar (nest) a modelos clásicos, expandiendo sus limitaciones. Las diferencias clave son:

#### vs. El Modelo de Bass Clásico (1969)
*   **Mercado Potencial Fijo vs. Endógeno:** En el modelo clásico de Bass, el mercado potencial total ($M$ o $m$) es una constante estática desde el instante $t=0$. En este modelo, el mercado potencial $M_{xi}(t)$ **crece dinámicamente** a lo largo del tiempo a medida que la utilidad de la innovación aumenta por los efectos de red.
*   **Fuentes de Influencia:** Bass asume que la difusión solo se acelera por el "boca a boca" local (la base instalada local). Este modelo argumenta que la adopción también se acelera observando a usuarios extranjeros (efecto cross-country) o a usuarios de tecnologías complementarias (efecto cross-product).
*   **Explicación del "Takeoff":** En Bass tradicional, el despegue inicial (Takeoff) está dictado rígidamente por $p$ y $q$. Este modelo proporciona una justificación para el crecimiento lento inicial y el efecto "palo de hockey": la difusión solo se acelera violentamente cuando las tres redes (local, extranjera, complementaria) alcanzan una masa crítica que expande el mercado potencial de golpe.

#### vs. Modelo de Dekimpe et al. (1998, 2000)
*   El modelo de Dekimpe es un caso particular (restricción) de este modelo. En Dekimpe, el mercado potencial es una fracción constante de la población, es decir, asume que no hay efectos de red crecientes ($\gamma_x = \widetilde{\gamma}_x = \widehat{\gamma}_{xy} = 0$). En tal caso, el modelo actual colapsa a $C_{xi}(t) = 1 - \theta_x$, volviéndose idéntico al de Dekimpe.

#### vs. Modelos de Difusión Multi-País (ej. Putsis et al. 1997, Talukdar et al. 2002)
*   Estos modelos capturan el desbordamiento internacional (*spillover* / efecto *cross-country*), reconociendo que lo que ocurre en un país afecta a otro. Sin embargo, **ignoran las interacciones entre productos**. Estudian productos "aislados" (ej. microondas, lavadoras). El modelo propuesto aquí demuestra que para tecnologías como PC/Internet o Hardware/Software, la difusión internacional no puede explicarse sin considerar el hardware complementario.

#### vs. Modelos de Efectos de Red Indirectos o Dual Market (ej. Stremersch et al. 2007, Bayus 1987)
*   Existen modelos previos que evalúan cómo las ventas de hardware afectan al software y viceversa. Sin embargo, toda esa investigación empírica previa se realizó **exclusivamente a nivel de un solo país**. El aporte radical de Ladrón-de-Guevara y Putsis es introducir una matriz que cruza tanto fronteras de productos como fronteras geográficas simultáneamente en una sola ecuación de verosimilitud (FIML).