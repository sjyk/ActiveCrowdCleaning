USE_CROWD = false; % Use crowd majority votes or gt labels?
NUM_ITERS = 10; % Number of points to evaluate at (after first point)
BUDGET = 1000; % Number of tasks to get gt labels for
ACTIVE_BOOTSTRAP = BUDGET / NUM_ITERS; % Number of initial samples to use for active learning
ACTIVE_STEPSIZE = BUDGET / NUM_ITERS; % Number of additional points to add at each active learning iteration.
RANDOM_SEED = 50; % random seed for sampling

% Load the dataset:
% V: crowd votes on each tweet (cols 1-4 are votes, col 5 is majority)
% dataset: bag-of-words features for each tweet (columns 3 to end)
% gt: ground truth labels for the tweets
load tweet_dataset.mat;
if USE_CROWD
    labels = V(:, 5);
else
    labels = gt;
end
step_size = ACTIVE_STEPSIZE;
rng(RANDOM_SEED);

% run the active learning upfront to avoid recomputation
disp('Precomputing active learning data...');
rng(RANDOM_SEED); % reset the random state
[all_active_predictions, active_eval] = active_learn(dataset, labels, ACTIVE_BOOTSTRAP, ACTIVE_STEPSIZE, BUDGET);
disp('Done!');

active_learning_plt = [];
passive_learning_plt = [];
rawsc_plt = [];
nsc_active_plt = [];
nsc_passive_plt = [];
learning_X = [];
rawsc_X = [];
nsc_X = [];
disp('Trading off between learning budget and sampling budget...')
for k = 0:NUM_ITERS
    disp(['Starting iteration ', num2str(k), '/', num2str(NUM_ITERS)]);
    sample_budget = BUDGET - (k * step_size);
    learning_budget = BUDGET - sample_budget;
    disp(['Learning budget: ', num2str(learning_budget), ... 
        '. Sample budget: ', num2str(sample_budget)]);
    
    X = k * 100 / NUM_ITERS;
    
    if learning_budget ~= 0
        learning_X = [learning_X X];
        
        % pull out the active learning data for this iter
        active_predictions = all_active_predictions(:, k);
        active_learning_plt = [active_learning_plt active_eval(k)];
    
        % train a passive model
        rng(RANDOM_SEED); % reset the random state
        passive_predictions = passive_learn(dataset, labels, learning_budget);
        passive_learning_plt = [passive_learning_plt eval_model_sum(passive_predictions, labels)];
    end
    
    if sample_budget ~= 0
        rawsc_X = [rawsc_X X];
        
        % compute the rawsc sum
        rng(RANDOM_SEED); % reset the random state
        rawsc_plt = [rawsc_plt eval_sc_sum(rawsc_sum(labels, sample_budget), labels)];
    end
    
    if learning_budget ~= 0 && sample_budget ~= 0
        nsc_X = [nsc_X X];
        
        % compute the nsc sum with the active predictions as the "dirty" data.
        rng(RANDOM_SEED); % reset the random state
        nsc_active_plt = [nsc_active_plt eval_sc_sum(nsc_sum(active_predictions, labels, sample_budget), labels)];
    
        % compute the nsc sum with the passive predictions as the "dirty" data.
        rng(RANDOM_SEED); % reset the random state
        nsc_passive_plt = [nsc_passive_plt eval_sc_sum(nsc_sum(passive_predictions, labels, sample_budget), labels)];
    end
end
disp('Done!');

figure;
plot(learning_X, active_learning_plt, 'gs-', ...
     learning_X, passive_learning_plt, 'rs-', ...
     rawsc_X, rawsc_plt, 'bs-', ...
     nsc_X, nsc_active_plt, 'ks-', ...
     nsc_X, nsc_passive_plt, 'cs-')
 xlabel('Percent of budget allocated to learning vs. sampling')
 ylabel('Error in sum computation')
 title(['Learning vs. Sampling tradeoff with fixed budget of ', num2str(BUDGET)]);