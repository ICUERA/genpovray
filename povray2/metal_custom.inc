//******************************************************

// some micro normals

#declare P_Micro1 = pigment {
   granite turbulence 0
   color_map {
     [0.0 rgb 0.3]
     [1.0 rgb 0.7]
   }
   scale 0.003
}


#declare P_Micro2 = pigment {
   onion turbulence 0.5
   color_map{
     [0.0  color rgb 1.00]
     [0.45 color rgb 0.99]
     [0.55 color rgb 0.96]
     [1.0  color rgb 0.95]
   }
   scale 0.01
}



#declare P_Macro1 = pigment {
   crackle turbulence 1
   color_map {
     [0.00 rgb 0.3]
     [0.01 rgb 0.3]
     [0.02 rgb 0.7]
     [1.00 rgb 0.7]
   }
   scale 0.3
}

// "micro"-normals for blurred reflection - to get some highlights
#macro P_Polish(Polish)
   pigment_pattern {
     average
     pigment_map {
       [1 P_Micro1 translate x*20]
       [1 P_Micro1 translate y*20]
       [1 P_Micro1 translate z*20]
       [1 P_Micro2 translate -x*20]
       [1 P_Micro2 translate -y*20]
       [1 P_Micro2 translate -z*20]
     }
   }
   1 - Polish
#end


// "macro"-normals for scratches and dents
#macro P_Dents(Dents)
   pigment_pattern {
     average
     pigment_map {
       [1 P_Macro1 translate y*10]
       [1 P_Macro1 translate z*10]
     }
   }
   Dents
#end


// averaged normals
#macro N_Pattern(Polish, Dents)
   normal {
     average
     normal_map {
       [1 P_Polish(Polish)]
       [1 P_Dents(Dents)]
     }
   }
#end



// MATERIAL MACROS

#macro MaterialGold(Polish, Dents)
   material {
     texture {
       pigment {rgb <0.9927, 0.6952, 0.3302>}
       N_Pattern(Polish, Dents)
       finish {
         ambient 0  diffuse 1-0.7280
         specular 0  brilliance 3
         reflection {0.0 1.0 fresnel on metallic}
         conserve_energy
       }
     }
     interior {ior 2.83}
   }
#end


#macro MaterialSilver(Polish, Dents)
   material {
     texture {
       pigment {rgb <0.9284, 0.9016, 0.8678>}
       N_Pattern(Polish, Dents)
       finish {
         ambient 0  diffuse 1-0.9001
         specular 0 brilliance 3
         reflection {0.0 1.0 fresnel on metallic}
         conserve_energy
       }
     }
     interior {ior 3.64}
   }
#end


#macro MaterialCopper(Polish, Dents)
   material {
     texture {
       pigment {rgb <0.7802, 0.2985, 0.1078>}
       N_Pattern(Polish, Dents)
       finish {
         ambient 0  diffuse 1-0.3832
         specular 0  brilliance 2.4
         reflection {0.0 1.0 fresnel on metallic}
         conserve_energy
       }
     }
     interior {ior 3.26}
   }
#end

#declare c_ALUMINUM = rgb <0.89, 0.91, 0.91>;
#declare c_BRASS_COOL = rgb <0.80, 0.80, 0.35>;
#declare c_BRASS = rgb <0.80, 0.65, 0.30>;
#declare c_BRASS_WARM = rgb <0.80, 0.55, 0.25>;
#declare c_BRONZE_NEW = rgb <0.80, 0.50, 0.25>;  //polished, no patina
#declare c_BRONZE_WARM = rgb <0.45, 0.30, 0.15>;
#declare c_BRONZE = rgb <0.45, 0.35, 0.15>;
#declare c_BRONZE_COOL = rgb <0.45, 0.40, 0.15>;
#declare c_CHROME = rgb <0.61, 0.61, 0.65>;      //duplex Ni + Cr
#declare c_COPPER = rgb <0.80, 0.45, 0.35>;
#declare c_GOLD = rgb <0.95, 0.775, 0.40>;
#declare c_PENNY = rgb <0.80, 0.45, 0.25>;       //"penny bronze" 5% Zn
#declare c_SILVER = rgb <0.96, 0.96, 0.92>;
#declare c_SILVER_COIN = rgb <0.66, 0.63, 0.57>; //75% Cu + 25% Ni
#declare c_STAINLESS = rgb 0.49;
#declare c_STAINLESS_WARM = rgb <0.51, 0.51, 0.47>;
#declare c_STEEL = rgb <0.61, 0.59, 0.54>;
#declare c_ZINC = rgb <0.78, 0.82, 0.80>;


//******************************************************