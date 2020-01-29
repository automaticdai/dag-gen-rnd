function D = dag_gen(dagDepth, spanSize, contProb, spanProb)

%% Define parameters
% dagDepth = 4;
% spanSize = 2;
% 
% contProb = 0.5;
% spanProb = 0.4;
joinProb = 1 - contProb - spanProb;

%% Main
s = [];
t = [];

s_ = 1;
n = 1;
candi = [s_];
type = 1;
% Loop
for i = 1:dagDepth - 1
    candi_new = [];
    for j = 1:numel(candi)
        a = candi(j);
        
        seed = rand();
        if seed < spanProb
            % span
            type = 1;
            for i = 1:spanSize            
                n = n + 1;
                s = [s a];
                t = [t n];
                candi_new = [candi_new n];
            end
        elseif seed < spanProb + contProb
            % cont
            type = 2;
            n = n + 1;
            s = [s a];
            t = [t n];
            candi_new = [candi_new n];
        else
            % join
            if (type ~= 3)
                n = n + 1;
            end
            
            if ((j+1) <= numel(candi))
                b = candi(j+1);

                s = [s a b];
                t = [t n n];

                candi_new = [candi_new n];
            else
                % cont
                s = [s a];
                t = [t n];
                candi_new = [candi_new n];
            end
            
            type = 3;
        end
    end
    
    candi = candi_new;
end

% Finish
% n = n + 1;
% for k = 1:numel(candi)
%     a = candi(k);
%     s = [s a];
%     t = [t n];
% end

D = digraph(s,t);
D = simplify(D);

end
