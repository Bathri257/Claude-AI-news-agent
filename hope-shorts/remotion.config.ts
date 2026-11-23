import {Config} from '@remotion/cli/config';
Config.setBrowserExecutable(process.env.REMOTION_BROWSER || null);
Config.setConcurrency(2);
