var Bar: integer;

var x: float;

for Bar := 14 to BarCount - 1 do

begin

  if not LastPositionActive then

  begin

    if PriceClose( Bar ) > SMA( Bar, #Close, 13 ) then

      if PriceClose( Bar ) < PriceClose( Bar - 1 ) then

        if ADX( Bar, 14 ) > 18 then

          if ATR( Bar, 13 ) / SMA( Bar, #Close, 13 ) > 0.01 then

          begin

            x := PriceClose( Bar ) + 0.5 * ( PriceHigh( Bar ) - PriceLow( Bar ) );

            if x < PriceHigh( Bar ) then

            begin

              try

                if x > PriceOpen( Bar + 1 ) then

              except

              end;

                BuyAtStop( Bar + 1, x, '' );

            end;

          end;

  end;

  if LastPositionActive then

    SellAtLimit( Bar + 1, PriceHigh( Bar ), LastPosition, '' );

end;