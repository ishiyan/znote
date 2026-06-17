# Dominant Cycle

**By John F. Ehlers**

- **Downloaded from:** [Mesa Software — Dominant Cycle](https://www.mesasoftware.com/papers/Dominant%20Cycle.pdf)

---

```easylanguage
{
Dominant Cycle
(C) 2026 John F. Ehlers
}
Inputs:
LowerBound(10),
UpperBound(40),
WindowLength(27);

Vars:
HP(0),
LP(0),
RMS(0),
Real(0),
ROC(0),
QRMS(0),
Imag(0),
Angle(0),
DC(0);

HP = $HighPass(Close, UpperBound);
LP = $SuperSmoother(HP, LowerBound);
RMS = $RMS(LP, 100);
If RMS <> 0 Then Real = LP / RMS;
ROC = Real - Real[1];
QRMS = $RMS(ROC, 100);
If QRMS <> 0 Then Imag = ROC / QRMS;

//Compute the angle as an arctangent function
If Real <> 0 Then Angle = 90 - Arctangent(Imag / Real);

//Resolve Arctangent ambiguity
If Real < 0 Then Angle = Angle - 180;

//compensate for filter lag / prediction
If Angle > 180 Then Angle = Angle - 360;

//angle cannot go backwards
If Angle < Angle[1] and Angle[1] - Angle < 270 Then Angle = Angle[1];

//Find DeltaAngle and eliminate outliers
If Angle <> Angle[1] Then DC = 360 / (Angle - Angle[1]);
If DC > 50 Then DC = 50;
If DC < 8 Then DC = 8;
Plot1($Hann(DC, WindowLength));
```

---

## BibTeX

```bibtex
@misc{ehlers_dominant_cycle,
  author       = {John F. Ehlers},
  title        = {Dominant Cycle},
  year         = {2026},
  howpublished = {online},
  url          = {https://www.mesasoftware.com/papers/Dominant%20Cycle.pdf}
}
```
