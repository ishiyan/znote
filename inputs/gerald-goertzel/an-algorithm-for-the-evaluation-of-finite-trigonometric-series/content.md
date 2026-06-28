# An Algorithm for the Evaluation of Finite Trigonometric Series

- **Author:** Gerald Goertzel
- **Affiliation:** Nuclear Development Corporation of America, White Plains, N. Y.
- **Publication:** *The American Mathematical Monthly*, Vol. 65, No. 1 (Jan., 1958), pp. 34--35
- **Publisher:** Mathematical Association of America
- **Source:** <http://www.jstor.org/stable/2310304>

---

The algorithm described below enables one to obtain the simultaneous numerical evaluation of $C = \sum_{0}^{N} a_k \cos kx$ and $S = \sum_{1}^{N} a_k \sin kx$ for given $a_k$, $\cos x$, and $\sin x$. Tables for $\sin kx$ and $\cos kx$ are not needed and only about $N$ multiplications and about $2N$ additions or subtractions are required, so the method may be of interest to programmers of digital computers.

The algorithm is defined by

$$U_{N+2} = U_{N+1} = 0;$$

$$U_k = a_k + 2 \cos x \, U_{k+1} - U_{k+2}, \qquad k = N, N-1, \ldots, 1.$$

$$C = a_0 + U_1 \cos x - U_2, \qquad S = U_1 \sin x.$$

To establish this result, consider

$$V_k = \sum_{j=k}^{N} a_j \sin(j - k + 1)x; \qquad k = 1, \ldots, N,$$

$$V_{N+1} = V_{N+2} = 0.$$

Then

$$a_k \sin x + 2 \cos x \, V_{k+1} - V_{k+2}$$

$$= a_k \sin x + \sum_{j=k+1}^{N} a_j \bigl[ 2 \cos x \, \sin(j-k)x - \sin(j-k-1)x \bigr]$$

$$= a_k \sin x + \sum_{j=k+1}^{N} a_j \sin(j-k+1)x = V_k,$$

whence $V_k = U_k \sin x$ and, in particular, $S = V_1 = U_1 \sin x$. Furthermore

$$a_0 \sin x + V_1 \cos x - V_2 = a_0 \sin x + \sum_{j=1}^{N} a_j \bigl[ \cos x \, \sin jx - \sin(j-1)x \bigr]$$

$$= a_0 \sin x + \sum_{j=1}^{N} a_j \cos jx \, \sin x = C \sin x,$$

whence $C = a_0 + U_1 \cos x - U_2$.

---

## BibTeX

```bibtex
@article{goertzel1958algorithm,
  author    = {Gerald Goertzel},
  title     = {An Algorithm for the Evaluation of Finite Trigonometric Series},
  journal   = {The American Mathematical Monthly},
  volume    = {65},
  number    = {1},
  pages     = {34--35},
  year      = {1958},
  month     = jan,
  publisher = {Mathematical Association of America},
  doi       = {10.2307/2310304},
  url       = {http://www.jstor.org/stable/2310304},
}
```
